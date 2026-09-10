OPENQASM 3.0;
include "stdgates.inc";
gate ccx_o0 _gate_q_0, _gate_q_1, _gate_q_2 {
  x _gate_q_0;
  x _gate_q_1;
  ccx _gate_q_0, _gate_q_1, _gate_q_2;
  x _gate_q_0;
  x _gate_q_1;
}
gate ccx_o1 _gate_q_0, _gate_q_1, _gate_q_2 {
  x _gate_q_1;
  ccx _gate_q_0, _gate_q_1, _gate_q_2;
  x _gate_q_1;
}
qubit[11] q;
cx q[0], q[2];
cx q[1], q[3];
ccx_o0 q[2], q[3], q[7];
cx q[1], q[3];
cx q[0], q[2];
cx q[0], q[4];
cx q[1], q[5];
ccx_o0 q[4], q[5], q[8];
cx q[1], q[5];
cx q[0], q[4];
ccx_o0 q[7], q[8], q[9];
cx q[2], q[4];
cx q[3], q[5];
ccx_o0 q[4], q[5], q[10];
cx q[3], q[5];
cx q[2], q[4];
ccx_o1 q[9], q[10], q[6];
cx q[2], q[4];
cx q[3], q[5];
ccx_o0 q[4], q[5], q[10];
cx q[3], q[5];
cx q[2], q[4];
ccx_o0 q[7], q[8], q[9];
cx q[0], q[4];
cx q[1], q[5];
ccx_o0 q[4], q[5], q[8];
cx q[1], q[5];
cx q[0], q[4];
cx q[0], q[2];
cx q[1], q[3];
ccx_o0 q[2], q[3], q[7];
cx q[1], q[3];
cx q[0], q[2];
