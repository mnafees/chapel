/*
 * Copyright 2021 Hewlett Packard Enterprise Development LP
 * Other additional copyright holders may be indicated within.
 *
 * The entirety of this work is licensed under the Apache License,
 * Version 2.0 (the "License"); you may not use this file except
 * in compliance with the License.
 *
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef CHPL_UTIL_MEMORY_H
#define CHPL_UTIL_MEMORY_H

#include <memory>

namespace chpl {

/**
 owned<T> is just a synonym for 'std::unique_ptr<T>'.
 It is shorter and uses the Chapel term for it.
 */
template<typename T>
  using owned = std::unique_ptr<T>;
/**
 give a raw pointer to an owned<T> to manage it.
 */
template<typename T>
static inline owned<T> toOwned(T* takeFrom) {
  return owned<T>(takeFrom);
}

} // end namespace chpl

#endif
