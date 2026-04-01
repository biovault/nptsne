Version 2.0.0
-----------------
Supports python 3.10, 3.11, 3.12, 3.13, 3.14 on Windows, Ubuntu (using manylinux_2_28) and Macos (restricted to arm64).

Changelog 2.0.0
~~~~~~~~~~~~~~~
- Using the latest HDILib iteration that gives cross-platform Vulkan driver support.
- Vulkan drivers (or other drivers) can be selected on the tSNE instance.
- The Vulkan driver is now the default on MacOS giving improved performance.
- tSNE over the Vulkan driver may be faster for 10^5 points and less. For very 
  large numbers of points the OpenGL driver (with compute shader) is about 20% faster. 