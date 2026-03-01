#!/usr/bin/env python3
"""
Workflow 构建器 - 修改基础 workflow
"""

import json
import copy
import random
from pathlib import Path


class WorkflowBuilder:
    """Workflow 构建器"""
    
    def __init__(self, base_workflow_path=None):
        """
        初始化 Workflow 构建器
        
        Args:
            base_workflow_path: 基础 workflow 文件路径，默认使用内置路径
        """
        if base_workflow_path is None:
            # 默认路径
            script_dir = Path(__file__).parent.parent
            base_workflow_path = script_dir / "workflows" / "base-workflow.json"
        
        self.base_workflow_path = Path(base_workflow_path)
        self.base_workflow = self._load_base_workflow()
    
    def _load_base_workflow(self) -> dict:
        """加载基础 workflow"""
        if not self.base_workflow_path.exists():
            raise FileNotFoundError(
                f"Base workflow not found: {self.base_workflow_path}\n"
                "Please ensure the base workflow file exists."
            )
        
        with open(self.base_workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _generate_seed(self) -> int:
        """生成随机种子"""
        return random.randint(1, 999999999999999)
    
    def build(self, positive_prompt: str, negative_prompt: str, seed: int = None) -> dict:
        """
        构建完整的 workflow
        
        Args:
            positive_prompt: 正面 prompt
            negative_prompt: 负面 prompt
            seed: 随机种子（可选，默认随机生成）
        
        Returns:
            完整的 workflow 字典
        """
        if seed is None:
            seed = self._generate_seed()
        
        # 深拷贝基础 workflow
        workflow = copy.deepcopy(self.base_workflow)
        
        # 包装成 ComfyUI API 格式（如果没有 prompt 键）
        if "prompt" not in workflow:
            workflow = {"prompt": workflow}
        
        prompt_data = workflow["prompt"]
        
        # 修改正面 prompt (节点 52 - CLIPTextEncode Positive)
        if "52" in prompt_data:
            prompt_data["52"]["inputs"]["text"] = positive_prompt
        else:
            print("Warning: Node 52 not found in workflow")
        
        # 修改负面 prompt (节点 38 - CLIPTextEncode Negative)
        if "38" in prompt_data:
            prompt_data["38"]["inputs"]["text"] = negative_prompt
        else:
            print("Warning: Node 38 not found in workflow")
        
        # 修改第一轮的种子 (节点 61 - KSampler First Pass)
        if "61" in prompt_data:
            prompt_data["61"]["inputs"]["seed"] = seed
        else:
            print("Warning: Node 61 not found in workflow")
        
        # 修改第二轮的种子 (节点 51 - KSampler Refiner)
        if "51" in prompt_data:
            prompt_data["51"]["inputs"]["seed"] = self._generate_seed()
        else:
            print("Warning: Node 51 not found in workflow")
        
        return workflow
    
    def build_simple(self, positive_prompt: str, negative_prompt: str) -> dict:
        """
        简化版构建（只修改 prompt，不修改种子）
        
        Args:
            positive_prompt: 正面 prompt
            negative_prompt: 负面 prompt
        
        Returns:
            完整的 workflow 字典
        """
        workflow = copy.deepcopy(self.base_workflow)
        prompt_data = workflow.get("prompt", {})
        
        # 修改正面 prompt
        if "52" in prompt_data:
            prompt_data["52"]["inputs"]["text"] = positive_prompt
        
        # 修改负面 prompt
        if "38" in prompt_data:
            prompt_data["38"]["inputs"]["text"] = negative_prompt
        
        return workflow


# 便捷函数
def build_workflow(positive: str, negative: str, seed: int = None, base_path=None) -> dict:
    """构建 workflow 的便捷函数"""
    builder = WorkflowBuilder(base_path)
    return builder.build(positive, negative, seed)


if __name__ == "__main__":
    # 测试
    builder = WorkflowBuilder()
    
    workflow = builder.build(
        positive_prompt="masterpiece, 1girl, happy, smiling",
        negative_prompt="bad quality, ugly"
    )
    
    print("Workflow built successfully!")
    print(f"Nodes: {len(workflow.get('prompt', {}))}")
    
    # 检查修改是否成功
    prompt_data = workflow.get("prompt", {})
    if "52" in prompt_data:
        print(f"Node 52 text: {prompt_data['52']['inputs']['text'][:50]}...")
    if "61" in prompt_data:
        print(f"Node 61 seed: {prompt_data['61']['inputs']['seed']}")