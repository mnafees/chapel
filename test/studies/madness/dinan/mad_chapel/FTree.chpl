record Coeff {
    var dom  : domain(1);
    var data : [dom] real;
    var valid: bool = true;
}

class FTree {
    var order    : int;
    var coeffDom = [0..order-1];
    var idx_t    : 2*int;         // FIXME: Can't write domain(2*int)

    var indices: domain(idx_t);   // Indexed by 2-tuples of integers
    var nodes  : [indices] Coeff; // Associative Mapping: (:int, :int) => Coeff


    def initialize() {
        if order == 0 then
            halt("FTree must be initialized with an order > 0");
    }


    // Access an element in the associative domain.  If the element
    // doesn't exist it will be created.
    def this(lvl: int, idx: int) var {
        //writeln("FTree: accessing (", lvl, ", ", idx, ")");
        if !indices.member((lvl, idx)) {
            //writeln("        creating (", lvl, ", ", idx, ")");
            indices += ((lvl, idx));
            nodes[(lvl, idx)] = Coeff(coeffDom);
        }

        nodes[(lvl, idx)].valid = true;
        return nodes[(lvl, idx)].data;
    }


    def has_coeffs(lvl: int, idx: int) {
        if indices.member((lvl, idx)) then
          return nodes[(lvl, idx)].valid;
        else return false;
    }

    // Remove an element from the associative domain.  If the element
    // does not exist, it is ignored.
    def remove(lvl: int, idx: int) {
        //writeln("FTree:  removing (", lvl, ", ", idx, ")");
        if indices.member((lvl, idx)) then
            //indices.remove((lvl, idx));
            nodes[(lvl, idx)].valid = false;
    }
}


def main() {
    var f = FTree(2);

    for (i, j) in [0..2, 0..2] do
        f[i, j] = (i, j);


    for (i, j) in [0..2, 0..2] do
        writeln("(",i,", ",j,") = ", f[i, j]);
}
