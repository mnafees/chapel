config const n = 10;
var a = 1;

proc main() {
  test(a, a);
  writeln(a);
}

proc test(ref a, ref b) {
  for i in 1..n {
    a += b;
  }
}
