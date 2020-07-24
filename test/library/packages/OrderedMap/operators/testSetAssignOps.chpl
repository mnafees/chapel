use OrderedMap;

var m0 = new orderedMap(int, int);
var m1 = new orderedMap(int, int);
var m2 = new orderedMap(int, int);

m0[1] = 1;
m0[2] = 2;
m0[3] = 3;
m1 = m0;
m2[1] = -1;
m2[3] = -3;
m2[5] = -5;

m1 += m2; writeln(m1.toArray().sorted()); m1 = m0;
m1 |= m2; writeln(m1.toArray().sorted()); m1 = m0;
m1 &= m2; writeln(m1.toArray().sorted()); m1 = m0;
m1 -= m2; writeln(m1.toArray().sorted()); m1 = m0;
m1 ^= m2; writeln(m1.toArray().sorted()); m1 = m0;

