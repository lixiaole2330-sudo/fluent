# Fluent 自动化

面向本地 Ansys Fluent 2025 R2 的 PyFluent 配置入口。GitHub 保存代码，计算在已安装 Fluent 且许可证有效的电脑执行。

## 安装

使用 Python 3.11（不要使用 Python 3.7）：

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 求解

将现有算例放入 inputs/model.cas.h5，复制并修改 configs/solver.example.json。

```powershell
.\.venv\Scripts\python.exe fluent_automation.py configs/solver.example.json --check
.\.venv\Scripts\python.exe fluent_automation.py configs/solver.example.json
```

默认保持已有算例设置、不重新初始化、不迭代。将 initialize 设置为 true 可混合初始化；iterations 指定稳态迭代次数。瞬态计算应使用专用 journal。settings 使用 Fluent 原生设置树，可配置 setup 下的 models、materials、boundary_conditions，以及 solution 下的 methods、controls 等。边界名称必须与实际算例一致，错误设置会报错。

settings 示例（仅适用于具有 inlet 速度入口的算例）：

```json
{"setup":{"boundary_conditions":{"velocity_inlet":{"inlet":{"momentum":{"velocity":{"value":1.0}}}}}}}
```

此示例不是通用物理工况，请根据单位、材料、流态和实际边界调整。已有算例的其余设置保持不变。

## 网格自动化

在 Fluent 2025 R2 中为具体几何录制并验证 meshing.jou，放入 inputs/，执行 configs/meshing.example.json。journal 应包含几何导入、尺寸、边界层、体网格、质量检查和网格保存步骤，输入输出建议使用绝对路径。入口以 meshing 模式自动执行该 journal；当前没有附带可用于任意几何的网格策略。网格完成后另用求解配置执行计算。

每次运行输出独立 runs 子目录；求解保存 result.cas.h5 / result.dat.h5 和日志。completed.json 仅表示命令完成，不代表收敛或物理结果正确。许可证、网格质量和收敛须在实际算例上验证。

## 当前验证范围

代码入口与配置静态校验；尚未完成真实几何的网格和求解端到端验证。需提供几何/算例及工况后完善专用模板。

官方资料：https://fluent.docs.pyansys.com/version/stable/
