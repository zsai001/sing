#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
规则导入导出管理器
Rule Import Export Manager
"""

import json
from typing import Dict, Any
from pathlib import Path
from utils import Logger


class RuleImportExportManager:
    """规则导入导出管理器"""
    
    def __init__(self, config_dir: Path, logger: Logger):
        self.config_dir = config_dir
        self.logger = logger
    
    def export_rules(self, routing_config: Dict[str, Any]):
        """导出规则"""
        export_file = self.config_dir / "routing_rules_export.json"
        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(routing_config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"✓ 规则已导出到: {export_file}")
        except Exception as e:
            self.logger.error(f"导出失败: {e}")
    
    def import_rules(self, routing_config: Dict[str, Any]):
        """导入规则"""
        import_file = input("请输入要导入的文件路径: ").strip()
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # 合并规则
            if 'rule_sets' in imported_config:
                routing_config.setdefault('rule_sets', {})
                routing_config['rule_sets'].update(imported_config['rule_sets'])
                self.logger.info("✓ 规则导入成功")
            else:
                self.logger.error("导入文件格式不正确")
        except Exception as e:
            self.logger.error(f"导入失败: {e}")
    
    def export_rule_set(self, rule_id: str, rule_set: Dict[str, Any]):
        """导出单个规则集"""
        export_file = self.config_dir / f"rule_set_{rule_id}.json"
        try:
            export_data = {
                "rule_sets": {
                    rule_id: rule_set
                }
            }
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"✓ 规则集 {rule_id} 已导出到: {export_file}")
        except Exception as e:
            self.logger.error(f"导出规则集失败: {e}")
    
    def backup_rules(self, routing_config: Dict[str, Any]):
        """备份当前规则"""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.config_dir / f"routing_backup_{timestamp}.json"
        
        try:
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(routing_config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"✓ 规则已备份到: {backup_file}")
            return backup_file
        except Exception as e:
            self.logger.error(f"备份失败: {e}")
            return None
    
    def restore_from_backup(self, routing_config: Dict[str, Any]):
        """从备份恢复规则"""
        backup_files = list(self.config_dir.glob("routing_backup_*.json"))
        
        if not backup_files:
            self.logger.warn("未找到备份文件")
            return
        
        print()
        print("可用的备份文件:")
        for i, backup_file in enumerate(backup_files, 1):
            print(f"  {i}. {backup_file.name}")
        
        try:
            choice = int(input("请选择备份文件编号: ").strip()) - 1
            if 0 <= choice < len(backup_files):
                backup_file = backup_files[choice]
                
                with open(backup_file, 'r', encoding='utf-8') as f:
                    backup_config = json.load(f)
                
                routing_config.clear()
                routing_config.update(backup_config)
                self.logger.info(f"✓ 已从备份恢复: {backup_file.name}")
            else:
                self.logger.error("无效选择")
        except (ValueError, json.JSONDecodeError) as e:
            self.logger.error(f"恢复失败: {e}")
    
    def validate_rule_format(self, rule_data: Dict[str, Any]) -> bool:
        """验证规则格式"""
        if not isinstance(rule_data, dict):
            return False
        
        if 'rule_sets' not in rule_data:
            return False
        
        rule_sets = rule_data['rule_sets']
        if not isinstance(rule_sets, dict):
            return False
        
        for rule_id, rule_set in rule_sets.items():
            if not isinstance(rule_set, dict):
                return False
            
            # 检查必要字段
            if 'rules' not in rule_set:
                return False
            
            if not isinstance(rule_set['rules'], list):
                return False
            
            # 检查每个规则
            for rule in rule_set['rules']:
                if not isinstance(rule, dict):
                    return False
                
                if 'outbound' not in rule:
                    return False
        
        return True 