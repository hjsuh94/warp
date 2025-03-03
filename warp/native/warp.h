/** Copyright (c) 2022 NVIDIA CORPORATION.  All rights reserved.
 * NVIDIA CORPORATION and its licensors retain all intellectual property
 * and proprietary rights in and to this software, related documentation
 * and any modifications thereto.  Any use, reproduction, disclosure or
 * distribution of this software and related documentation without an express
 * license agreement from NVIDIA CORPORATION is strictly prohibited.
 */

#pragma once

// defines all crt + builtin types
#include "builtin.h"

// this is the core runtime API exposed on the DLL level
extern "C"
{
    WP_API int init();
    //WP_API void shutdown();

    // whether Warp was compiled with CUDA support
    WP_API int is_cuda_enabled();
    // whether Warp was compiled with enhanced CUDA compatibility
    WP_API int is_cuda_compatibility_enabled();
    // whether Warp was compiled with CUTLASS support
    WP_API int is_cutlass_enabled();
    // whether Warp was compiled with debug support
    WP_API int is_debug_enabled();

    WP_API uint16_t float_to_half_bits(float x);
    WP_API float half_bits_to_float(uint16_t u);

    WP_API void* alloc_host(size_t s);
    WP_API void* alloc_pinned(size_t s);
    WP_API void* alloc_device(void* context, size_t s);
    WP_API void* alloc_temp_device(void* context, size_t s);

    WP_API void free_host(void* ptr);
    WP_API void free_pinned(void* ptr);
    WP_API void free_device(void* context, void* ptr);
    WP_API void free_temp_device(void* context, void* ptr);

    // all memcpys are performed asynchronously
    WP_API void memcpy_h2h(void* dest, void* src, size_t n);
    WP_API void memcpy_h2d(void* context, void* dest, void* src, size_t n);
    WP_API void memcpy_d2h(void* context, void* dest, void* src, size_t n);
    WP_API void memcpy_d2d(void* context, void* dest, void* src, size_t n);
    WP_API void memcpy_peer(void* context, void* dest, void* src, size_t n);

    // all memsets are performed asynchronously
    WP_API void memset_host(void* dest, int value, size_t n);
    WP_API void memset_device(void* context, void* dest, int value, size_t n);
    
    // takes srcsize bytes starting at src and repeats them n times at dst (writes srcsize * n bytes in total):
    WP_API void memtile_host(void* dest, const void* src, size_t srcsize, size_t n);
    WP_API void memtile_device(void* context, void* dest, const void* src, size_t srcsize, size_t n);

	WP_API uint64_t bvh_create_host(wp::vec3* lowers, wp::vec3* uppers, int num_items);
	WP_API void bvh_destroy_host(uint64_t id);
    WP_API void bvh_refit_host(uint64_t id);

	WP_API uint64_t bvh_create_device(void* context, wp::vec3* lowers, wp::vec3* uppers, int num_items);
	WP_API void bvh_destroy_device(uint64_t id);
    WP_API void bvh_refit_device(uint64_t id);

    // create a user-accessible copy of the mesh, it is the 
    // users responsibility to keep-alive the points/tris data for the duration of the mesh lifetime
	WP_API uint64_t mesh_create_host(wp::array_t<wp::vec3> points, wp::array_t<wp::vec3> velocities, wp::array_t<int> tris, int num_points, int num_tris, int support_winding_number);
	WP_API void mesh_destroy_host(uint64_t id);
    WP_API void mesh_refit_host(uint64_t id);

	WP_API uint64_t mesh_create_device(void* context, wp::array_t<wp::vec3> points, wp::array_t<wp::vec3> velocities, wp::array_t<int> tris, int num_points, int num_tris, int support_winding_number);
	WP_API void mesh_destroy_device(uint64_t id);
    WP_API void mesh_refit_device(uint64_t id);

    WP_API uint64_t hash_grid_create_host(int dim_x, int dim_y, int dim_z);
    WP_API void hash_grid_reserve_host(uint64_t id, int num_points);
    WP_API void hash_grid_destroy_host(uint64_t id);
    WP_API void hash_grid_update_host(uint64_t id, float cell_width, const wp::vec3* positions, int num_points);

    WP_API uint64_t hash_grid_create_device(void* context, int dim_x, int dim_y, int dim_z);
    WP_API void hash_grid_reserve_device(uint64_t id, int num_points);
    WP_API void hash_grid_destroy_device(uint64_t id);
    WP_API void hash_grid_update_device(uint64_t id, float cell_width, const wp::vec3* positions, int num_points);

    WP_API bool cutlass_gemm(int compute_capability, int m, int n, int k, const char* datatype,
                             const void* a, const void* b, const void* c, void* d, float alpha, float beta,
                             bool row_major_a, bool row_major_b, bool allow_tf32x3_arith, int batch_count);

    WP_API uint64_t volume_create_host(void* buf, uint64_t size);
    WP_API void volume_get_buffer_info_host(uint64_t id, void** buf, uint64_t* size);
    WP_API void volume_get_tiles_host(uint64_t id, void** buf, uint64_t* size);
    WP_API void volume_destroy_host(uint64_t id);

    WP_API uint64_t volume_create_device(void* context, void* buf, uint64_t size);
    WP_API uint64_t volume_f_from_tiles_device(void* context, void* points, int num_points, float voxel_size, float bg_value, float tx, float ty, float tz, bool points_in_world_space);
    WP_API uint64_t volume_v_from_tiles_device(void* context, void* points, int num_points, float voxel_size, float bg_value_x, float bg_value_y, float bg_value_z, float tx, float ty, float tz, bool points_in_world_space);
    WP_API uint64_t volume_i_from_tiles_device(void* context, void* points, int num_points, float voxel_size, int bg_value, float tx, float ty, float tz, bool points_in_world_space);
    WP_API void volume_get_buffer_info_device(uint64_t id, void** buf, uint64_t* size);
    WP_API void volume_get_tiles_device(uint64_t id, void** buf, uint64_t* size);
    WP_API void volume_destroy_device(uint64_t id);

    WP_API void volume_get_voxel_size(uint64_t id, float* dx, float* dy, float* dz);
    
    WP_API uint64_t marching_cubes_create_device(void* context);
    WP_API void marching_cubes_destroy_device(uint64_t id);
    WP_API int marching_cubes_surface_device(uint64_t id, const float* field, int nx, int ny, int nz, float threshold, wp::vec3* verts, int* triangles, int max_verts, int max_tris, int* out_num_verts, int* out_num_tris);

    // generic copy supporting non-contiguous arrays
    WP_API size_t array_copy_host(void* dst, void* src, int dst_type, int src_type, int elem_size);
    WP_API size_t array_copy_device(void* context, void* dst, void* src, int dst_type, int src_type, int elem_size);

    // generic fill for non-contiguous arrays
    WP_API void array_fill_host(void* arr, int arr_type, const void* value, int value_size);
    WP_API void array_fill_device(void* context, void* arr, int arr_type, const void* value, int value_size);

    WP_API void array_inner_float_host(uint64_t a, uint64_t b, uint64_t out, int count, int stride_a, int stride_b, int type_len);
    WP_API void array_inner_double_host(uint64_t a, uint64_t b, uint64_t out, int count, int stride_a, int stride_b, int type_len);
    WP_API void array_inner_float_device(uint64_t a, uint64_t b, uint64_t out, int count, int stride_a, int stride_b, int type_len);
    WP_API void array_inner_double_device(uint64_t a, uint64_t b, uint64_t out, int count, int stride_a, int stride_b, int type_len);

    WP_API void array_sum_float_device(uint64_t a, uint64_t out, int count, int stride, int type_len);
    WP_API void array_sum_float_host(uint64_t a, uint64_t out, int count, int stride, int type_len);
    WP_API void array_sum_double_host(uint64_t a, uint64_t out, int count, int stride, int type_len);
    WP_API void array_sum_double_device(uint64_t a, uint64_t out, int count, int stride, int type_len);

    WP_API void array_scan_int_host(uint64_t in, uint64_t out, int len, bool inclusive);
    WP_API void array_scan_float_host(uint64_t in, uint64_t out, int len, bool inclusive);

    WP_API void array_scan_int_device(uint64_t in, uint64_t out, int len, bool inclusive);
    WP_API void array_scan_float_device(uint64_t in, uint64_t out, int len, bool inclusive);

    WP_API void radix_sort_pairs_int_host(uint64_t keys, uint64_t values, int n);
    WP_API void radix_sort_pairs_int_device(uint64_t keys, uint64_t values, int n);

    WP_API void runlength_encode_int_host(uint64_t values, uint64_t run_values, uint64_t run_lengths, uint64_t run_count, int n);
    WP_API void runlength_encode_int_device(uint64_t values, uint64_t run_values, uint64_t run_lengths, uint64_t run_count, int n);

    WP_API int bsr_matrix_from_triplets_float_host(
        int rows_per_block,
        int cols_per_block,
        int row_count,
        int nnz,
        uint64_t tpl_rows,
        uint64_t tpl_columns,
        uint64_t tpl_values,
        uint64_t bsr_offsets,
        uint64_t bsr_columns,
        uint64_t bsr_values);
    WP_API int bsr_matrix_from_triplets_double_host(
        int rows_per_block,
        int cols_per_block,
        int row_count,
        int nnz,
        uint64_t tpl_rows,
        uint64_t tpl_columns,
        uint64_t tpl_values,
        uint64_t bsr_offsets,
        uint64_t bsr_columns,
        uint64_t bsr_values);

    WP_API int bsr_matrix_from_triplets_float_device(
        int rows_per_block,
        int cols_per_block,
        int row_count,
        int nnz,
        uint64_t tpl_rows,
        uint64_t tpl_columns,
        uint64_t tpl_values,
        uint64_t bsr_offsets,
        uint64_t bsr_columns,
        uint64_t bsr_values);
    WP_API int bsr_matrix_from_triplets_double_device(
        int rows_per_block,
        int cols_per_block,
        int row_count,
        int nnz,
        uint64_t tpl_rows,
        uint64_t tpl_columns,
        uint64_t tpl_values,
        uint64_t bsr_offsets,
        uint64_t bsr_columns,
        uint64_t bsr_values);

    WP_API void bsr_transpose_float_host(int rows_per_block, int cols_per_block,
        int row_count, int col_count, int nnz,
        uint64_t bsr_offsets, uint64_t bsr_columns,
        uint64_t bsr_values,
        uint64_t transposed_bsr_offsets,
        uint64_t transposed_bsr_columns,
        uint64_t transposed_bsr_values);
    WP_API void bsr_transpose_double_host(int rows_per_block, int cols_per_block,
        int row_count, int col_count, int nnz,
        uint64_t bsr_offsets, uint64_t bsr_columns,
        uint64_t bsr_values,
        uint64_t transposed_bsr_offsets,
        uint64_t transposed_bsr_columns,
        uint64_t transposed_bsr_values);

    WP_API void bsr_transpose_float_device(int rows_per_block, int cols_per_block,
        int row_count, int col_count, int nnz,
        uint64_t bsr_offsets, uint64_t bsr_columns,
        uint64_t bsr_values,
        uint64_t transposed_bsr_offsets,
        uint64_t transposed_bsr_columns,
        uint64_t transposed_bsr_values);
    WP_API void bsr_transpose_double_device(int rows_per_block, int cols_per_block,
        int row_count, int col_count, int nnz,
        uint64_t bsr_offsets, uint64_t bsr_columns,
        uint64_t bsr_values,
        uint64_t transposed_bsr_offsets,
        uint64_t transposed_bsr_columns,
        uint64_t transposed_bsr_values);


    WP_API int cuda_driver_version();   // CUDA driver version
    WP_API int cuda_toolkit_version();  // CUDA Toolkit version used to build Warp
    WP_API bool cuda_driver_is_initialized();

    WP_API int nvrtc_supported_arch_count();
    WP_API void nvrtc_supported_archs(int* archs);

    WP_API int cuda_device_get_count();
    WP_API void* cuda_device_primary_context_retain(int ordinal);
    WP_API void cuda_device_primary_context_release(int ordinal);
    WP_API const char* cuda_device_get_name(int ordinal);
    WP_API int cuda_device_get_arch(int ordinal);
    WP_API int cuda_device_is_uva(int ordinal);
    WP_API int cuda_device_is_memory_pool_supported(int ordinal);

    WP_API void* cuda_context_get_current();
    WP_API void cuda_context_set_current(void* context);
    WP_API void cuda_context_push_current(void* context);
    WP_API void cuda_context_pop_current();
    WP_API void* cuda_context_create(int device_ordinal);
    WP_API void cuda_context_destroy(void* context);
    WP_API int cuda_context_get_device_ordinal(void* context);
    WP_API int cuda_context_is_primary(void* context);
    WP_API int cuda_context_is_memory_pool_supported(void* context);
    WP_API void* cuda_context_get_stream(void* context);
    WP_API void cuda_context_set_stream(void* context, void* stream);
    WP_API int cuda_context_can_access_peer(void* context, void* peer_context);
    WP_API int cuda_context_enable_peer_access(void* context, void* peer_context);

    // ensures all device side operations have completed in the current context
    WP_API void cuda_context_synchronize(void* context);

    // return cudaError_t code
    WP_API uint64_t cuda_context_check(void* context);

    WP_API void* cuda_stream_create(void* context);
    WP_API void cuda_stream_destroy(void* context, void* stream);
    WP_API void cuda_stream_synchronize(void* context, void* stream);
    WP_API void* cuda_stream_get_current();
    WP_API void cuda_stream_wait_event(void* context, void* stream, void* event);
    WP_API void cuda_stream_wait_stream(void* context, void* stream, void* other_stream, void* event);

    WP_API void* cuda_event_create(void* context, unsigned flags);
    WP_API void cuda_event_destroy(void* context, void* event);
    WP_API void cuda_event_record(void* context, void* event, void* stream);

    WP_API void cuda_graph_begin_capture(void* context);
    WP_API void* cuda_graph_end_capture(void* context);
    WP_API void cuda_graph_launch(void* context, void* graph);
    WP_API void cuda_graph_destroy(void* context, void* graph);

    WP_API size_t cuda_compile_program(const char* cuda_src, int arch, const char* include_dir, bool debug, bool verbose, bool verify_fp, bool fast_math, const char* output_file);

    WP_API void* cuda_load_module(void* context, const char* ptx);
    WP_API void cuda_unload_module(void* context, void* module);
    WP_API void* cuda_get_kernel(void* context, void* module, const char* name);
    WP_API size_t cuda_launch_kernel(void* context, void* kernel, size_t dim, int max_blocks, void** args);

    WP_API void cuda_set_context_restore_policy(bool always_restore);
    WP_API int cuda_get_context_restore_policy();

    WP_API void cuda_graphics_map(void* context, void* resource);
    WP_API void cuda_graphics_unmap(void* context, void* resource);
    WP_API void cuda_graphics_device_ptr_and_size(void* context, void* resource, uint64_t* ptr, size_t* size);
    WP_API void* cuda_graphics_register_gl_buffer(void* context, uint32_t gl_buffer, unsigned int flags);
    WP_API void cuda_graphics_unregister_resource(void* context, void* resource);

} // extern "C"
 