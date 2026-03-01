#!/usr/bin/env python3
"""
CLI 工具 - 生成明日香表情包

Usage:
    python generate-emotion.py <emotion> [--count N]
    python generate-emotion.py list
    python generate-emotion.py stock
"""

import argparse
import sys
from pathlib import Path

# 添加项目路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from core.config_loader import get_config
from generators.image_generator import ImageGenerator
from managers.emotion_manager import EmotionManager


def list_emotions():
    """列出所有可用表情"""
    config = get_config()
    emotions = config.get('emotions', {})
    
    print("Available emotions:")
    print("-" * 50)
    for key, value in emotions.items():
        name = value.get('name', key) if isinstance(value, dict) else key
        print(f"  {key:12} - {name}")
    print("-" * 50)


def list_outfits():
    """列出所有可用衣服"""
    config = get_config()
    outfits = config.get('outfits', {})
    
    print("Available outfits:")
    print("-" * 70)
    for name, outfit in outfits.items():
        if isinstance(outfit, dict):
            weight = outfit.get('weight', 1)
            desc = outfit.get('description', '')[:45]
            print(f"  {name:15} (weight: {weight}) - {desc}")
    print("-" * 70)


def show_stock():
    """显示库存状态"""
    manager = EmotionManager()
    stocks = manager.get_all_stocks()
    stats = manager.get_stats()
    
    print("Current emotion stock:")
    print("-" * 60)
    print(f"{'Emotion':<12} {'Count':<8} {'Total Usage':<12} {'Avg Usage':<10}")
    print("-" * 60)
    
    for emotion in sorted(stocks.keys()):
        count = stocks[emotion]
        stat = stats.get(emotion, {})
        total_usage = stat.get('total_usage', 0)
        avg_usage = stat.get('avg_usage', 0)
        print(f"{emotion:<12} {count:<8} {total_usage:<12} {avg_usage:<10.1f}")
    
    print("-" * 60)


def generate(emotion: str, count: int = 1):
    """生成表情图片"""
    config = get_config()
    emotions = config.get('emotions', {})
    
    if emotion not in emotions:
        print(f"Error: Unknown emotion '{emotion}'")
        print(f"Run 'python generate-emotion.py list' to see available emotions.")
        sys.exit(1)
    
    generator = ImageGenerator(config)
    manager = EmotionManager()
    
    emotion_config = emotions[emotion]
    emotion_name = emotion_config.get('name', emotion) if isinstance(emotion_config, dict) else emotion
    
    print(f"Generating {count} '{emotion_name}' image(s)...")
    print("=" * 60)
    
    generated = []
    for i in range(count):
        print(f"\n[{i+1}/{count}] Generating...")
        
        path = generator.generate(emotion)
        
        if path:
            print(f"✓ Success: {path}")
            generated.append(path)
            
            # 添加到库存索引
            manager.add_emotion(emotion, path)
        else:
            print(f"✗ Failed")
    
    print("\n" + "=" * 60)
    print(f"Generated {len(generated)}/{count} image(s)")
    
    return generated


def main():
    parser = argparse.ArgumentParser(
        description="Generate Asuka emotion images using ComfyUI"
    )
    
    parser.add_argument(
        "emotion",
        nargs="?",
        help="Emotion type (happy, shy, angry, smug, sad, surprised, love)"
    )
    
    parser.add_argument(
        "--count", "-c",
        type=int,
        default=1,
        help="Number of images to generate (default: 1)"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all available emotions"
    )
    
    parser.add_argument(
        "--outfits",
        action="store_true",
        help="List all available outfits"
    )
    
    parser.add_argument(
        "--stock", "-s",
        action="store_true",
        help="Show current stock status"
    )
    
    args = parser.parse_args()
    
    # 处理列表命令
    if args.list:
        list_emotions()
        return
    
    if args.outfits:
        list_outfits()
        return
    
    if args.stock:
        show_stock()
        return
    
    # 检查 emotion 参数
    if not args.emotion:
        parser.print_help()
        sys.exit(1)
    
    # 生成图片
    generate(args.emotion, args.count)


if __name__ == "__main__":
    main()