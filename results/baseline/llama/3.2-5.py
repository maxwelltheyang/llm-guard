import ctypes

# Create a pointer to an integer
buf_ptr = ctypes.pointer(ctypes.c_int(0))

# Free the buffer when we're done with it
def free_buffer():
    ctypes.free(buf_ptr)
