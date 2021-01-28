#!/usr/bin/env python3

"""A script to generate FileCheck statements for 'opt' regression tests.

This script is a utility to update LLVM opt test cases with new
FileCheck patterns. It can either update all of the tests in the file or
a single test function.

Example usage:
$ update_test_checks.py --opt=../bin/opt test/foo.ll

Workflow:
1. Make a compiler patch that requires updating some number of FileCheck lines
   in regression test files.
2. Save the patch and revert it from your local work area.
3. Update the RUN-lines in the affected regression tests to look canonical.
   Example: "; RUN: opt < %s -instcombine -S | FileCheck %s"
4. Refresh the FileCheck lines for either the entire file or select functions by
   running this script.
5. Commit the fresh baseline of checks.
6. Apply your patch from step 1 and rebuild your local binaries.
7. Re-run this script on affected regression tests.
8. Check the diffs to ensure the script has done something reasonable.
9. Submit a patch including the regression test diffs for review.

A common pattern is to have the script insert complete checking of every
instruction. Then, edit it down to only check the relevant instructions.
The script is designed to make adding checks to a test case fast, it is *not*
designed to be authoratitive about what constitutes a good test!
"""

from __future__ import print_function

import argparse
import os  # Used to advertise this file's name ("autogenerated_note").
import re
import sys

from UpdateTestChecks import common


def main():
  from argparse import RawTextHelpFormatter
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)
  parser.add_argument('--opt-binary', default='opt',
                      help='The opt binary used to generate the test case')
  parser.add_argument(
      '--function', help='The function in the test file to update')
  parser.add_argument('-p', '--preserve-names', action='store_true',
                      help='Do not scrub IR names')
  parser.add_argument('--function-signature', action='store_true',
                      help='Keep function signature information around for the check line')
  parser.add_argument('--scrub-attributes', action='store_true',
                      help='Remove attribute annotations (#0) from the end of check line')
  parser.add_argument('tests', nargs='+')
  initial_args = common.parse_commandline_args(parser)

  script_name = os.path.basename(__file__)
  opt_basename = os.path.basename(initial_args.opt_binary)
  if not re.match(r'^opt(-\d+)?$', opt_basename):
    common.error('Unexpected opt name: ' + opt_basename)
    sys.exit(1)
  opt_basename = 'opt'

  for ti in common.itertests(initial_args.tests, parser,
                             script_name='utils/' + script_name):
    # If requested we scrub trailing attribute annotations, e.g., '#0', together with whitespaces
    if ti.args.scrub_attributes:
      common.SCRUB_TRAILING_WHITESPACE_TEST_RE = common.SCRUB_TRAILING_WHITESPACE_AND_ATTRIBUTES_RE
    else:
      common.SCRUB_TRAILING_WHITESPACE_TEST_RE = common.SCRUB_TRAILING_WHITESPACE_RE

    prefix_list = []
    for l in ti.run_lines:
      if '|' not in l:
        common.warn('Skipping unparseable RUN line: ' + l)
        continue

      (tool_cmd, filecheck_cmd) = tuple([cmd.strip() for cmd in l.split('|', 1)])
      common.verify_filecheck_prefixes(filecheck_cmd)
      if not tool_cmd.startswith(opt_basename + ' '):
        common.warn('Skipping non-%s RUN line: %s' % (opt_basename, l))
        continue

      if not filecheck_cmd.startswith('FileCheck '):
        common.warn('Skipping non-FileChecked RUN line: ' + l)
        continue

      tool_cmd_args = tool_cmd[len(opt_basename):].strip()
      tool_cmd_args = tool_cmd_args.replace('< %s', '').replace('%s', '').strip()

      check_prefixes = [item for m in
                        common.CHECK_PREFIX_RE.finditer(filecheck_cmd)
                        for item in m.group(1).split(',')]
      if not check_prefixes:
        check_prefixes = ['CHECK']

      # FIXME: We should use multiple check prefixes to common check lines. For
      # now, we just ignore all but the last.
      prefix_list.append((check_prefixes, tool_cmd_args))

    func_dict = {}
    for prefixes, _ in prefix_list:
      for prefix in prefixes:
        func_dict.update({prefix: dict()})
    for prefixes, opt_args in prefix_list:
      common.debug('Extracted opt cmd: ' + opt_basename + ' ' + opt_args)
      common.debug('Extracted FileCheck prefixes: ' + str(prefixes))

      raw_tool_output = common.invoke_tool(ti.args.opt_binary, opt_args, ti.path)
      common.build_function_body_dictionary(
              common.OPT_FUNCTION_RE, common.scrub_body, [],
              raw_tool_output, prefixes, func_dict, ti.args.verbose,
              ti.args.function_signature)

    is_in_function = False
    is_in_function_start = False
    prefix_set = set([prefix for prefixes, _ in prefix_list for prefix in prefixes])
    common.debug('Rewriting FileCheck prefixes:', str(prefix_set))
    output_lines = []
    for input_line_info in ti.iterlines(output_lines):
      input_line = input_line_info.line
      args = input_line_info.args
      if is_in_function_start:
        if input_line == '':
          continue
        if input_line.lstrip().startswith(';'):
          m = common.CHECK_RE.match(input_line)
          if not m or m.group(1) not in prefix_set:
            output_lines.append(input_line)
            continue

        # Print out the various check lines here.
        common.add_ir_checks(output_lines, ';', prefix_list, func_dict,
                             func_name, args.preserve_names, args.function_signature)
        is_in_function_start = False

      if is_in_function:
        if common.should_add_line_to_output(input_line, prefix_set):
          # This input line of the function body will go as-is into the output.
          # Except make leading whitespace uniform: 2 spaces.
          input_line = common.SCRUB_LEADING_WHITESPACE_RE.sub(r'  ', input_line)
          output_lines.append(input_line)
        else:
          continue
        if input_line.strip() == '}':
          is_in_function = False
        continue

      # If it's outside a function, it just gets copied to the output.
      output_lines.append(input_line)

      m = common.IR_FUNCTION_RE.match(input_line)
      if not m:
        continue
      func_name = m.group(1)
      if args.function is not None and func_name != args.function:
        # When filtering on a specific function, skip all others.
        continue
      is_in_function = is_in_function_start = True

    common.debug('Writing %d lines to %s...' % (len(output_lines), ti.path))

    with open(ti.path, 'wb') as f:
      f.writelines(['{}\n'.format(l).encode('utf-8') for l in output_lines])


if __name__ == '__main__':
  main()
