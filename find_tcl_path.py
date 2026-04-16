import tkinter
import os

# 创建 Tk 实例
root = tkinter.Tk()

# 获取 Tcl/Tk 库路径
tcl_lib = root.tk.exprstring('$tcl_library')
tk_lib = root.tk.exprstring('$tk_library')

print(f"Tcl 库路径: {tcl_lib}")
print(f"Tk 库路径: {tk_lib}")

# 检查路径是否存在
print(f"Tcl 路径存在: {os.path.exists(tcl_lib)}")
print(f"Tk 路径存在: {os.path.exists(tk_lib)}")

# 获取 Tcl 版本
tcl_version = root.tk.eval('info version')
print(f"Tcl 版本: {tcl_version}")

root.destroy()
