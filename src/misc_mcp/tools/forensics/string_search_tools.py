"""
字符串搜索工具
提供在文件中搜索字符串的功能
"""
import os
import subprocess
from misc_mcp.server import mcp


@mcp.tool()
def search_string_in_file_by_strings(file_path: str, search_text: str, min_length: int = 4) -> str:
    """
    使用 strings 命令在文件中搜索指定字符串（支持二进制文件）
    
    Args:
        file_path: 要搜索的文件路径
        search_text: 要搜索的字符串
        min_length: strings 命令的最小字符串长度（默认 4）
        
    Returns:
        搜索结果，包含匹配的行和上下文
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return f"错误: 文件不存在 - {file_path}"
        
        # 检查文件是否可读
        if not os.path.isfile(file_path):
            return f"错误: 不是一个有效的文件 - {file_path}"
        
        # 使用 strings 命令提取可打印字符串
        strings_cmd = ['strings', '-n', str(min_length), file_path]
        strings_result = subprocess.run(
            strings_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if strings_result.returncode != 0:
            return f"strings 命令执行失败: {strings_result.stderr}"
        
        # 在提取的字符串中搜索目标文本
        lines = strings_result.stdout.splitlines()
        matches = []
        
        for i, line in enumerate(lines):
            if search_text in line:
                # 收集匹配行及其上下文
                context_before = lines[max(0, i-2):i]
                context_after = lines[i+1:min(len(lines), i+3)]
                
                match_info = {
                    'line_number': i + 1,
                    'matched_line': line,
                    'context_before': context_before,
                    'context_after': context_after
                }
                matches.append(match_info)
        
        if not matches:
            return f"未找到匹配的字符串: '{search_text}'"
        
        # 格式化输出结果
        result = f"在文件 {file_path} 中找到 {len(matches)} 处匹配:\n\n"
        
        for idx, match in enumerate(matches, 1):
            result += f"=== 匹配 {idx} (行号: {match['line_number']}) ===\n"
            
            # 显示前置上下文
            if match['context_before']:
                result += "上文:\n"
                for line in match['context_before']:
                    result += f"  {line}\n"
            
            # 显示匹配行
            result += f">>> {match['matched_line']}\n"
            
            # 显示后置上下文
            if match['context_after']:
                result += "下文:\n"
                for line in match['context_after']:
                    result += f"  {line}\n"
            
            result += "\n"
        
        return result.strip()
        
    except subprocess.TimeoutExpired:
        return "错误: strings 命令执行超时"
    except Exception as e:
        return f"搜索失败: {str(e)}"


@mcp.tool()
def search_string_in_file_by_code(file_path: str, search_text: str, case_sensitive: bool = True, show_context: bool = True) -> str:
    """
    使用 Python 代码在文件中搜索指定字符串（支持文本和二进制文件）
    
    Args:
        file_path: 要搜索的文件路径
        search_text: 要搜索的字符串
        case_sensitive: 是否区分大小写（默认 True）
        show_context: 是否显示上下文（默认 True）
        
    Returns:
        搜索结果，包含匹配的位置和内容
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return f"错误: 文件不存在 - {file_path}"
        
        # 检查文件是否可读
        if not os.path.isfile(file_path):
            return f"错误: 不是一个有效的文件 - {file_path}"
        
        matches = []
        
        # 首先尝试以文本模式读取
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            search_target = search_text if case_sensitive else search_text.lower()
            
            for line_num, line in enumerate(lines, 1):
                line_to_check = line if case_sensitive else line.lower()
                
                if search_target in line_to_check:
                    match_info = {
                        'line_number': line_num,
                        'matched_line': line.rstrip('\n'),
                        'context_before': [],
                        'context_after': []
                    }
                    
                    # 收集上下文
                    if show_context:
                        # 前两行
                        for i in range(max(0, line_num-3), line_num-1):
                            if i < len(lines):
                                match_info['context_before'].append(lines[i].rstrip('\n'))
                        
                        # 后两行
                        for i in range(line_num, min(len(lines), line_num+2)):
                            if i < len(lines):
                                match_info['context_after'].append(lines[i].rstrip('\n'))
                    
                    matches.append(match_info)
        
        except UnicodeDecodeError:
            # 如果文本模式失败，尝试二进制模式
            with open(file_path, 'rb') as f:
                content = f.read()
            
            search_bytes = search_text.encode('utf-8', errors='ignore')
            
            # 在二进制内容中搜索
            offset = 0
            while True:
                pos = content.find(search_bytes, offset)
                if pos == -1:
                    break
                
                # 提取匹配位置周围的内容
                context_start = max(0, pos - 50)
                context_end = min(len(content), pos + len(search_bytes) + 50)
                context = content[context_start:context_end]
                
                # 尝试解码为可读文本
                try:
                    context_str = context.decode('utf-8', errors='replace')
                except:
                    context_str = repr(context)
                
                match_info = {
                    'byte_offset': pos,
                    'matched_content': search_text,
                    'context': context_str
                }
                matches.append(match_info)
                
                offset = pos + 1
        
        if not matches:
            return f"未找到匹配的字符串: '{search_text}'"
        
        # 格式化输出结果
        result = f"在文件 {file_path} 中找到 {len(matches)} 处匹配:\n\n"
        
        for idx, match in enumerate(matches, 1):
            if 'line_number' in match:
                # 文本文件模式
                result += f"=== 匹配 {idx} (行号: {match['line_number']}) ===\n"
                
                # 显示前置上下文
                if show_context and match['context_before']:
                    result += "上文:\n"
                    for line in match['context_before']:
                        result += f"  {line}\n"
                
                # 显示匹配行
                result += f">>> {match['matched_line']}\n"
                
                # 显示后置上下文
                if show_context and match['context_after']:
                    result += "下文:\n"
                    for line in match['context_after']:
                        result += f"  {line}\n"
            else:
                # 二进制文件模式
                result += f"=== 匹配 {idx} (字节偏移: {match['byte_offset']}) ===\n"
                result += f"匹配内容: {match['matched_content']}\n"
                result += f"上下文: {match['context']}\n"
            
            result += "\n"
        
        return result.strip()
        
    except PermissionError:
        return f"错误: 没有权限读取文件 - {file_path}"
    except Exception as e:
        return f"搜索失败: {str(e)}"

