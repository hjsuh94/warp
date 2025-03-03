import numpy as np
import unittest

import warp as wp
from warp.tests.test_base import *

wp.init()


class gemm_test_bed_runner:
    def __init__(self, dtype, device):
        self.dtype = dtype
        self.device = device

    def alloc(self, m, n, k, batch_count):
        rng = np.random.default_rng(42)
        low = -4.5
        high = 3.5
        if batch_count == 1:
            A = wp.array2d(
                np.ceil(rng.uniform(low=low, high=high, size=(m, k))),
                dtype=self.dtype,
                device=self.device,
                requires_grad=True
            )
            B = wp.array2d(
                np.ceil(rng.uniform(low=low, high=high, size=(k, n))),
                dtype=self.dtype,
                device=self.device,
                requires_grad=True
            )
            C = wp.array2d(
                np.ceil(rng.uniform(low=low, high=high, size=(m, n))),
                dtype=self.dtype,
                device=self.device,
                requires_grad=True
            )
            D = wp.array2d(
                np.zeros((m, n)),
                dtype=self.dtype,
                device=self.device,
                requires_grad=True)
        else:
            A = wp.array3d(
                np.ceil(rng.uniform(low=low, high=high, size=(batch_count, m, k))),
                dtype=self.dtype,
                device=self.device,
                requires_grad=True
            )
            B = wp.array3d(
                np.ceil(rng.uniform(low=low, high=high, size=(batch_count, k, n))),
                dtype=self.dtype,
                device=self.device,
                requires_grad=True
            )
            C = wp.array3d(
                np.ceil(rng.uniform(low=low, high=high, size=(batch_count, m, n))),
                dtype=self.dtype,
                device=self.device,
                requires_grad=True
            )
            D = wp.array3d(
                np.zeros((batch_count, m, n)),
                dtype=self.dtype,
                device=self.device,
                requires_grad=True
            )
        return A, B, C, D

    def run_and_verify(self, m, n, k, batch_count, alpha, beta):
        A, B, C, D = self.alloc(m, n, k, batch_count)
        ones = wp.zeros_like(D)
        ones.fill_(1.0)
        
        if batch_count == 1:
            tape = wp.Tape()
            with tape:
                wp.matmul(A, B, C, D, alpha, beta, False, self.device)
            tape.backward(grads={D : ones})
            
            D_np = alpha * (A.numpy() @ B.numpy()) + beta * C.numpy()
            assert np.array_equal(D_np, D.numpy())

            adj_A_np = alpha * np.matmul(ones.numpy(), B.numpy().transpose())
            adj_B_np = alpha * (A.numpy().transpose() @ ones.numpy())
            adj_C_np = beta * ones.numpy()

        else:
            tape = wp.Tape()
            with tape:
                wp.batched_matmul(A, B, C, D, alpha, beta, False, self.device)
            tape.backward(grads={D : ones})
            
            D_np = alpha * np.matmul(A.numpy(), B.numpy()) + beta * C.numpy()
            assert np.array_equal(D_np, D.numpy())

            adj_A_np = alpha * np.matmul(ones.numpy(), B.numpy().transpose((0, 2, 1)))
            adj_B_np = alpha * np.matmul(A.numpy().transpose((0, 2, 1)), ones.numpy())
            adj_C_np = beta * ones.numpy()

        assert np.array_equal(adj_A_np, A.grad.numpy())
        assert np.array_equal(adj_B_np, B.grad.numpy())
        assert np.array_equal(adj_C_np, C.grad.numpy())

    def run(self):
        Ms = [64, 128, 512]
        Ns = [64, 128, 512]
        Ks = [64, 128, 512]
        batch_counts = [1, 4]
        betas = [0.0, 1.0]
        alpha = 1.0

        for batch_count in batch_counts:
            for m in Ms:
                for n in Ns:
                    for k in Ks:
                        for beta in betas:
                            self.run_and_verify(m, n, k, batch_count, alpha, beta)


class gemm_test_bed_runner_transpose:
    def __init__(self, dtype, device):
        self.dtype = dtype
        self.device = device

    def alloc(self, m, n, k, batch_count):
        rng = np.random.default_rng(42)
        low = -4.5
        high = 3.5
        if batch_count == 1:
            A = wp.array2d(
                np.ceil(rng.uniform(low=low, high=high, size=(m, k))),
                dtype=self.dtype,
                device=self.device,
                requires_grad=True
            )
            B = wp.array2d(
                np.ceil(rng.uniform(low=low, high=high, size=(k, n))),
                dtype=self.dtype,
                device=self.device,
                requires_grad=True
            )
            C = wp.array2d(
                np.ceil(rng.uniform(low=low, high=high, size=(m, n))),
                dtype=self.dtype,
                device=self.device,
                requires_grad=True
            )
            D = wp.array2d(
                np.zeros((m, n)),
                dtype=self.dtype,
                device=self.device,
                requires_grad=True
            )
            AT = wp.array2d(
                A.numpy().transpose([1, 0]),
                dtype=self.dtype,
                device=self.device,
                requires_grad=True
            )
            BT = wp.array2d(
                B.numpy().transpose([1, 0]),
                dtype=self.dtype,
                device=self.device,
                requires_grad=True
            )
        else:
            A = wp.array3d(
                np.ceil(rng.uniform(low=low, high=high, size=(batch_count, m, k))),
                dtype=self.dtype,
                device=self.device,
                requires_grad=True
            )
            B = wp.array3d(
                np.ceil(rng.uniform(low=low, high=high, size=(batch_count, k, n))),
                dtype=self.dtype,
                device=self.device,
                requires_grad=True
            )
            C = wp.array3d(
                np.ceil(rng.uniform(low=low, high=high, size=(batch_count, m, n))),
                dtype=self.dtype,
                device=self.device,
                requires_grad=True
            )
            D = wp.array3d(
                np.zeros((batch_count, m, n)),
                dtype=self.dtype,
                device=self.device,
                requires_grad=True
            )
            AT = wp.array3d(
                A.numpy().transpose([0, 2, 1]),
                dtype=self.dtype,
                device=self.device,
                requires_grad=True
            )
            BT = wp.array3d(
                B.numpy().transpose([0, 2, 1]),
                dtype=self.dtype,
                device=self.device,
                requires_grad=True
            )
        return A, B, C, D, AT, BT

    def run_and_verify(self, m, n, k, batch_count, alpha, beta):
        A, B, C1, D1, AT1, BT1 = self.alloc(m, n, k, batch_count)
        C2 = wp.clone(C1)
        C3 = wp.clone(C1)
        D2 = wp.clone(D1)
        D3 = wp.clone(D1)
        AT2 = wp.clone(AT1)
        BT2 = wp.clone(BT1)
        ones1 = wp.zeros_like(D1)
        ones1.fill_(1.0)
        ones2 = wp.zeros_like(D2)
        ones2.fill_(1.0)
        ones3 = wp.zeros_like(D3)
        ones3.fill_(1.0)

        if batch_count == 1:
            ATT1 = AT1.transpose([1, 0])        
            BTT1 = BT1.transpose([1, 0])
            ATT2 = AT2.transpose([1, 0])        
            BTT2 = BT2.transpose([1, 0])
            tape = wp.Tape()
            with tape:
                wp.matmul(A, BTT1, C1, D1, alpha, beta, False, self.device)
                wp.matmul(ATT1, B, C2, D2, alpha, beta, False, self.device)
                wp.matmul(ATT2, BTT2, C3, D3, alpha, beta, False, self.device)
            tape.backward(grads={D1 : ones1, D2 : ones2, D3 : ones3})
            
            D_np = alpha * (A.numpy() @ B.numpy()) + beta * C1.numpy()
            assert np.array_equal(D_np, D1.numpy())
            assert np.array_equal(D_np, D2.numpy())
            assert np.array_equal(D_np, D3.numpy())

            adj_A_np = alpha * (ones1.numpy() @ B.numpy().transpose())
            adj_B_np = alpha * (A.numpy().transpose() @ ones1.numpy())
            adj_C_np = beta * ones1.numpy()

        else:
            ATT1 = AT1.transpose([0, 2, 1])        
            BTT1 = BT1.transpose([0, 2, 1])
            ATT2 = AT2.transpose([0, 2, 1])
            BTT2 = BT2.transpose([0, 2, 1])
            tape = wp.Tape()
            with tape:
                wp.batched_matmul(A, BTT1, C1, D1, alpha, beta, False, self.device)
                wp.batched_matmul(ATT1, B, C2, D2, alpha, beta, False, self.device)
                wp.batched_matmul(ATT2, BTT2, C3, D3, alpha, beta, False, self.device)
            tape.backward(grads={D1 : ones1, D2 : ones2, D3 : ones3})
            
            D_np = alpha * np.matmul(A.numpy(), B.numpy()) + beta * C1.numpy()
            assert np.array_equal(D_np, D1.numpy())
            assert np.array_equal(D_np, D2.numpy())
            assert np.array_equal(D_np, D3.numpy())

            adj_A_np = alpha * np.matmul(ones1.numpy(), B.numpy().transpose((0, 2, 1)))
            adj_B_np = alpha * np.matmul(A.numpy().transpose((0, 2, 1)), ones1.numpy())
            adj_C_np = beta * ones1.numpy()

        assert np.array_equal(adj_A_np, A.grad.numpy())
        assert np.array_equal(adj_A_np, ATT1.grad.numpy())
        assert np.array_equal(adj_A_np, ATT2.grad.numpy())
        assert np.array_equal(adj_B_np, B.grad.numpy())
        assert np.array_equal(adj_B_np, BTT1.grad.numpy())
        assert np.array_equal(adj_B_np, BTT2.grad.numpy())
        assert np.array_equal(adj_C_np, C1.grad.numpy())
        assert np.array_equal(adj_C_np, C2.grad.numpy())
        assert np.array_equal(adj_C_np, C3.grad.numpy())

    def run(self):
        m = 16
        n = 32
        k = 64
        batch_counts = [1, 4]
        beta = 1.0
        alpha = 1.0

        for batch_count in batch_counts:
            self.run_and_verify(m, n, k, batch_count, alpha, beta)


# NOTE: F16 tests are slow due to the performance of the reference numpy F16 matmuls performed on CPU.
def test_f16(test, device):
    gemm_test_bed_runner(wp.float16, device).run()
    gemm_test_bed_runner_transpose(wp.float16, device).run()


def test_f32(test, device):
    gemm_test_bed_runner(wp.float32, device).run()
    gemm_test_bed_runner_transpose(wp.float32, device).run()


def test_f64(test, device):
    gemm_test_bed_runner(wp.float64, device).run()
    gemm_test_bed_runner_transpose(wp.float64, device).run()


@wp.kernel
def matrix_sum_kernel(arr: wp.array2d(dtype=float), loss: wp.array(dtype=float)):
    i, j = wp.tid()
    wp.atomic_add(loss, 0, arr[i, j])


def test_tape(test, device):
    rng = np.random.default_rng(42)
    low = -4.5
    high = 3.5
    m = 64
    n = 128
    k = 256
    A = wp.array2d(
        np.ceil(rng.uniform(low=low, high=high, size=(m, k))), dtype=float, device=device, requires_grad=True
    )
    B = wp.array2d(
        np.ceil(rng.uniform(low=low, high=high, size=(k, n))), dtype=float, device=device, requires_grad=True
    )
    C = wp.array2d(
        np.ceil(rng.uniform(low=low, high=high, size=(m, n))), dtype=float, device=device, requires_grad=True
    )
    D = wp.array2d(np.zeros((m, n)), dtype=float, device=device, requires_grad=True)
    loss = wp.zeros(1, dtype=float, device=device, requires_grad=True)

    # test tape
    tape = wp.Tape()
    with tape:
        wp.matmul(A, B, C, D, device=device)
        wp.launch(matrix_sum_kernel, dim=(m, n), inputs=[D, loss], device=device)

    tape.backward(loss=loss)
    A_grad = A.grad.numpy()

    # test adjoint
    D.grad = wp.array2d(np.ones((m, n)), dtype=float, device=device)
    wp.adj_matmul(A, B, C, A.grad, B.grad, C.grad, D.grad, device=device)
    assert_np_equal(A_grad, A.grad.numpy())

    # test zero
    tape.zero()
    assert_array_equal(A.grad, wp.zeros_like(A))


def test_operator(test, device):
    rng = np.random.default_rng(42)
    low = -4.5
    high = 3.5
    m = 64
    n = 128
    k = 256
    A = wp.array2d(
        np.ceil(rng.uniform(low=low, high=high, size=(m, k))), dtype=float, device=device, requires_grad=True
    )
    B = wp.array2d(
        np.ceil(rng.uniform(low=low, high=high, size=(k, n))), dtype=float, device=device, requires_grad=True
    )
    loss = wp.zeros(1, dtype=float, device=device, requires_grad=True)

    # test tape
    tape = wp.Tape()
    with tape:
        D = A @ B
        wp.launch(matrix_sum_kernel, dim=(m, n), inputs=[D, loss], device=device)

    tape.backward(loss=loss)

    # test adjoint
    D.grad = wp.array2d(np.ones((m, n)), dtype=float, device=device)
    B_transpose = wp.array2d(B.transpose().numpy(), dtype=float, device=device)

    adj_A = D.grad @ B_transpose
    assert_array_equal(adj_A, A.grad)

    # test zero
    tape.zero()
    assert_array_equal(A.grad, wp.zeros_like(A))


def test_large_batch_count(test, device):
    rng = np.random.default_rng(42)
    low = -4.5
    high = 3.5
    m = 2
    n = 3
    k = 4
    batch_count = 65535 * 2 + int(65535 / 2)
    A = wp.array3d(
        np.ceil(rng.uniform(low=low, high=high, size=(batch_count, m, k))), dtype=float, device=device, requires_grad=True
    )
    B = wp.array3d(
        np.ceil(rng.uniform(low=low, high=high, size=(batch_count, k, n))), dtype=float, device=device, requires_grad=True
    )
    C = wp.array3d(
        np.ceil(rng.uniform(low=low, high=high, size=(batch_count, m, n))), dtype=float, device=device, requires_grad=True
    )
    D = wp.array3d(
        np.zeros((batch_count, m, n)), dtype=float, device=device, requires_grad=True
    )
    ones = wp.zeros_like(D)
    ones.fill_(1.0)

    alpha = 1.0
    beta = 1.0
    
    tape = wp.Tape()
    with tape:
        wp.batched_matmul(A, B, C, D, alpha=alpha, beta=beta, allow_tf32x3_arith=False, device=device)
    tape.backward(grads={D : ones})

    D_np = alpha * np.matmul(A.numpy(), B.numpy()) + beta * C.numpy()
    assert np.array_equal(D_np, D.numpy())
    
    adj_A_np = alpha * np.matmul(ones.numpy(), B.numpy().transpose((0, 2, 1)))
    adj_B_np = alpha * np.matmul(A.numpy().transpose((0, 2, 1)), ones.numpy())
    adj_C_np = beta * ones.numpy()

    assert np.array_equal(adj_A_np, A.grad.numpy())
    assert np.array_equal(adj_B_np, B.grad.numpy())
    assert np.array_equal(adj_C_np, C.grad.numpy())


def register(parent):
    devices = [d for d in get_test_devices()]

    class TestMatmul(parent):
        pass

    if devices:
        # check if CUTLASS is available
        from warp.context import runtime

        if runtime.core.is_cutlass_enabled():
            # add_function_test(TestMatmul, "test_f16", test_f16, devices=devices)
            add_function_test(TestMatmul, "test_f32", test_f32, devices=devices)
            add_function_test(TestMatmul, "test_f64", test_f64, devices=devices)
            add_function_test(TestMatmul, "test_tape", test_tape, devices=devices)
            add_function_test(TestMatmul, "test_operator", test_operator, devices=devices)
            add_function_test(TestMatmul, "test_large_batch_count", test_large_batch_count, devices=devices)
        else:
            print("Skipping matmul tests because CUTLASS is not supported in this build")

    return TestMatmul


if __name__ == "__main__":
    wp.build.clear_kernel_cache()
    _ = register(unittest.TestCase)
    unittest.main(verbosity=2, failfast=False)
