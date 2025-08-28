OPENQASM 3.0;
include "stdgates.inc";
qubit[4] q;
cx q[1], q[0];
cx q[2], q[1];
ccx q[0], q[1], q[3];
cx q[2], q[1];
cx q[1], q[0];
