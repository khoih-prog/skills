#!/usr/bin/env python3
"""
FIS 3.1 Lite - 子代理三角色流水线示例
Architect → Worker → Reviewer
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from subagent_lifecycle import SubAgentLifecycleManager, SubAgentRole

def main():
    print("=" * 60)
    print("🎭 FIS 3.1 Lite - 三角色流水线演示")
    print("=" * 60)
    
    # 创建管理器 (CyberMao 作为 Architect)
    manager = SubAgentLifecycleManager("cybermao")
    
    print("\n📋 阶段 1: Architect (设计)")
    print("-" * 40)
    print("任务: 设计 PTVF 滤波器算法")
    print("输出: 算法规范文档")
    
    print("\n📋 阶段 2: 发放工卡给 Worker")
    print("-" * 40)
    
    # 创建 Worker
    worker = manager.spawn(
        name="小毛-Worker-001",
        role=SubAgentRole.WORKER,
        task_description="实现 PTVF 滤波器算法：\n"
                        "1. 读取 SFCW B-Scan 数据\n"
                        "2. 应用 PTVF 滤波 (order=4)\n" 
                        "3. 输出增强后的微多普勒图\n"
                        "4. 生成性能报告",
        timeout_minutes=120,
        resources=["file_read", "file_write", "python_exec", "numpy", "matplotlib"]
    )
    
    print(f"✅ 工号: {worker['employee_id']}")
    print(f"✅ 工作区: {worker['workspace']['path']}")
    
    # 激活 Worker
    manager.activate(worker['employee_id'])
    print(f"✅ 状态: PENDING → ACTIVE")
    
    # 显示工卡
    print("\n" + manager.generate_badge(worker['employee_id']))
    
    print("\n📋 阶段 3: Worker 执行任务...")
    print("-" * 40)
    print("(Worker 在自己的工作区独立执行)")
    print("  - 读取输入数据")
    print("  - 执行 PTVF 算法")
    print("  - 生成输出文件")
    
    # 模拟 Worker 完成
    print("\n✅ Worker 任务完成!")
    
    print("\n📋 阶段 4: 发放工卡给 Reviewer")
    print("-" * 40)
    
    # 创建 Reviewer
    reviewer = manager.spawn(
        name="老毛-Reviewer-001",
        role=SubAgentRole.REVIEWER,
        task_description="审查 Worker-001 的 PTVF 实现：\n"
                        "1. 验证算法正确性\n"
                        "2. 检查代码规范\n"
                        "3. 确认输出文件完整\n"
                        "4. 给出通过/不通过结论",
        timeout_minutes=60,
        resources=["file_read", "code_review"]
    )
    
    manager.activate(reviewer['employee_id'])
    print(f"✅ 工号: {reviewer['employee_id']}")
    print(f"✅ 状态: ACTIVE")
    
    print("\n" + manager.generate_badge(reviewer['employee_id']))
    
    print("\n📋 阶段 5: Reviewer 审查...")
    print("-" * 40)
    print("  - 读取 Worker 输出")
    print("  - 技术验证")
    print("  - 规范检查")
    print("\n✅ Review 通过!")
    
    print("\n📋 阶段 6: Architect 验收")
    print("-" * 40)
    print("✅ 所有阶段完成，任务闭环!")
    
    # 终止子代理
    print("\n📋 阶段 7: 回收工卡")
    print("-" * 40)
    manager.terminate(worker['employee_id'], "completed")
    manager.terminate(reviewer['employee_id'], "completed")
    print(f"✅ {worker['employee_id']}: terminated")
    print(f"✅ {reviewer['employee_id']}: terminated")
    
    print("\n" + "=" * 60)
    print("🎉 三角色流水线演示完成!")
    print("=" * 60)
    
    # 列出所有活跃子代理
    active = manager.list_active()
    print(f"\n📊 当前活跃子代理: {len(active)}")
    for sa in active:
        print(f"  - {sa['employee_id']}: {sa['name']}")
    
    print("\n💡 实际使用:")
    print("  from subagent_lifecycle import SubAgentLifecycleManager")
    print("  manager = SubAgentLifecycleManager('cybermao')")
    print("  card = manager.spawn(name='...', role=..., task='...')")
    print("  print(manager.generate_badge(card['employee_id']))")

if __name__ == "__main__":
    main()
