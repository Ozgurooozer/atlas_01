"""
Hardware Abstraction Layer (Layer 0).

Hardware and OS abstraction. Engine does not know about pyglet/glfw/sdl.
Only knows about interfaces: IWindow, IGPUDevice, IFilesystem, IClock.
"""