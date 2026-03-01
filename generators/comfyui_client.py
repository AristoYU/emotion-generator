#!/usr/bin/env python3
"""
ComfyUI API 客户端
"""

import json
import time
import requests
from pathlib import Path
from typing import Optional, Dict, Any


class ComfyUIClient:
    """ComfyUI API 客户端"""
    
    def __init__(self, host: str = "localhost", port: int = 7860, timeout: int = 180):
        """
        初始化 ComfyUI 客户端
        
        Args:
            host: ComfyUI 主机地址
            port: ComfyUI 端口
            timeout: 请求超时时间（秒）
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{host}:{port}"
    
    def check_connection(self) -> bool:
        """检查 ComfyUI 连接是否正常"""
        try:
            response = requests.get(
                f"{self.base_url}/system_stats",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Connection check failed: {e}")
            return False
    
    def submit(self, workflow: Dict[str, Any]) -> str:
        """
        提交 workflow 到 ComfyUI
        
        Args:
            workflow: 完整的 workflow 字典
        
        Returns:
            prompt_id: 任务 ID
        
        Raises:
            requests.RequestException: 请求失败
        """
        url = f"{self.base_url}/prompt"
        
        # 确保格式正确
        if "prompt" not in workflow:
            payload = {"prompt": workflow}
        else:
            payload = workflow
        
        response = requests.post(
            url,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        prompt_id = result.get("prompt_id")
        
        if not prompt_id:
            raise ValueError(f"No prompt_id in response: {result}")
        
        return prompt_id
    
    def get_status(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务状态
        
        Args:
            prompt_id: 任务 ID
        
        Returns:
            任务状态字典，如果未找到返回 None
        """
        url = f"{self.base_url}/history"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            history = response.json()
            return history.get(prompt_id)
        except Exception as e:
            print(f"Error getting status: {e}")
            return None
    
    def is_completed(self, prompt_id: str) -> bool:
        """
        检查任务是否完成
        
        Args:
            prompt_id: 任务 ID
        
        Returns:
            是否完成
        """
        status = self.get_status(prompt_id)
        if not status:
            return False
        
        status_info = status.get("status", {})
        return status_info.get("completed", False)
    
    def wait_for_completion(
        self,
        prompt_id: str,
        timeout: Optional[int] = None,
        poll_interval: float = 2.0
    ) -> Optional[Dict[str, Any]]:
        """
        等待任务完成
        
        Args:
            prompt_id: 任务 ID
            timeout: 超时时间（秒），默认使用初始化时的 timeout
            poll_interval: 轮询间隔（秒）
        
        Returns:
            任务输出字典，如果超时返回 None
        """
        if timeout is None:
            timeout = self.timeout
        
        start_time = time.time()
        print(f"Waiting for completion... (timeout: {timeout}s)")
        
        while time.time() - start_time < timeout:
            status = self.get_status(prompt_id)
            
            if status:
                status_info = status.get("status", {})
                
                if status_info.get("completed"):
                    print("✓ Generation completed!")
                    return status.get("outputs")
                
                if status_info.get("status_str") == "error":
                    print(f"✗ Generation failed: {status_info}")
                    return None
            
            print(".", end="", flush=True)
            time.sleep(poll_interval)
        
        print("\n✗ Timeout!")
        return None
    
    def download_image(
        self,
        filename: str,
        save_path: str,
        subfolder: str = "",
        image_type: str = "temp"
    ) -> str:
        """
        下载生成的图片
        
        Args:
            filename: 文件名
            save_path: 保存路径
            subfolder: 子文件夹
            image_type: 图片类型 (temp/output)
        
        Returns:
            保存的文件路径
        """
        url = f"{self.base_url}/view"
        params = {
            "filename": filename,
            "subfolder": subfolder,
            "type": image_type
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        # 确保目录存在
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        return str(save_path)
    
    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态"""
        url = f"{self.base_url}/queue"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        return response.json()


if __name__ == "__main__":
    # 测试
    client = ComfyUIClient()
    
    print("Testing ComfyUI connection...")
    if client.check_connection():
        print("✓ Connection successful!")
        
        # 获取系统信息
        response = requests.get(f"{client.base_url}/system_stats")
        stats = response.json()
        print(f"ComfyUI version: {stats.get('system', {}).get('comfyui_version')}")
    else:
        print("✗ Connection failed!")