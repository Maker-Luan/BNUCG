#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
贝塞尔曲线交互程序 - 使用 tkinter (Python 标准库)
功能：
    - 鼠标左键：添加控制点（红色圆点）
    - 灰色虚线：控制多边形
    - 绿色曲线：贝塞尔曲线（德卡斯特里奥算法）
    - 键盘 C 键：清空所有控制点
    - 实时显示 FPS 和控制点数量
"""

import tkinter as tk
import math
import time

# 窗口尺寸
WIDTH, HEIGHT = 1100, 650

class BezierApp:
    def __init__(self, root):
        self.root = root
        root.title("贝塞尔曲线 - 鼠标左键加点 | C键清空")
        root.geometry(f"{WIDTH}x{HEIGHT}")
        root.resizable(False, False)
        
        # 画布
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg='white', highlightthickness=0)
        self.canvas.pack()
        
        # 控制点列表 (每个点为 (x, y))
        self.points = []
        
        # 曲线采样点数
        self.curve_samples = 300
        
        # 帧率计算相关
        self.fps = 0
        self.last_time = time.time()
        self.frame_count = 0
        
        # 绑定事件
        self.canvas.bind("<Button-1>", self.add_point)   # 鼠标左键添加点
        self.root.bind("<Key-c>", self.clear_points)    # 按 C 清空
        self.root.bind("<Key-C>", self.clear_points)    # 大写 C 同样处理
        
        # 启动动画循环 (刷新画面)
        self.update_animation()
        
    def add_point(self, event):
        """鼠标左键添加控制点 (边界限制)"""
        x = max(8, min(WIDTH-8, event.x))
        y = max(8, min(HEIGHT-8, event.y))
        self.points.append((x, y))
        
    def clear_points(self, event=None):
        """清空所有控制点"""
        self.points.clear()
        
    def de_casteljau(self, points, t):
        """德卡斯特里奥算法：给定控制点列表和参数 t，返回曲线上点的坐标"""
        if not points:
            return (0, 0)
        if len(points) == 1:
            return points[0]
        temp = list(points)
        while len(temp) > 1:
            new_temp = []
            for i in range(len(temp)-1):
                x = (1-t) * temp[i][0] + t * temp[i+1][0]
                y = (1-t) * temp[i][1] + t * temp[i+1][1]
                new_temp.append((x, y))
            temp = new_temp
        return temp[0]
    
    def get_bezier_curve_points(self, points, num_samples):
        """生成贝塞尔曲线上的所有点"""
        if len(points) < 2:
            return []
        curve = []
        for i in range(num_samples + 1):
            t = i / num_samples
            pt = self.de_casteljau(points, t)
            curve.append(pt)
        return curve
    
    def draw_dashed_line(self, x1, y1, x2, y2, dash_len=8, gap_len=4):
        """在 canvas 上绘制虚线 (通过重复绘制短线模拟)"""
        length = math.hypot(x2 - x1, y2 - y1)
        if length == 0:
            return
        dx = (x2 - x1) / length
        dy = (y2 - y1) / length
        cur_len = 0
        drawing = True
        while cur_len < length:
            start_x = x1 + dx * cur_len
            start_y = y1 + dy * cur_len
            end_len = min(cur_len + (dash_len if drawing else gap_len), length)
            end_x = x1 + dx * end_len
            end_y = y1 + dy * end_len
            if drawing:
                self.canvas.create_line(start_x, start_y, end_x, end_y, fill='gray', width=2, tags="temp")
            cur_len = end_len
            drawing = not drawing
    
    def draw_grid(self):
        """绘制浅色网格背景"""
        step = 30
        for x in range(0, WIDTH, step):
            self.canvas.create_line(x, 0, x, HEIGHT, fill='#e0e4ec', width=1, tags="temp")
        for y in range(0, HEIGHT, step):
            self.canvas.create_line(0, y, WIDTH, y, fill='#e0e4ec', width=1, tags="temp")
    
    def draw_control_polygon(self, points):
        """绘制灰色虚线控制多边形"""
        if len(points) < 2:
            return
        for i in range(len(points)-1):
            x1, y1 = points[i]
            x2, y2 = points[i+1]
            self.draw_dashed_line(x1, y1, x2, y2)
    
    def draw_bezier_curve(self, points):
        """绘制绿色贝塞尔曲线"""
        if len(points) < 2:
            return
        curve = self.get_bezier_curve_points(points, self.curve_samples)
        if len(curve) < 2:
            return
        # 将曲线点列表转换为平铺的坐标序列
        coords = []
        for pt in curve:
            coords.extend(pt)
        self.canvas.create_line(coords, fill='#3bc14a', width=3, smooth=True, tags="temp")
    
    def draw_control_points(self, points):
        """绘制红色控制点及编号"""
        for idx, (x, y) in enumerate(points):
            # 外红点
            self.canvas.create_oval(x-7, y-7, x+7, y+7, fill='#e34234', outline='black', width=1, tags="temp")
            # 白色内芯
            self.canvas.create_oval(x-3, y-3, x+3, y+3, fill='white', outline='', tags="temp")
            # 编号文字
            self.canvas.create_text(x, y-10, text=str(idx+1), fill='black', font=('Consolas', 10, 'bold'), tags="temp")
    
    def draw_info(self, fps, point_count):
        """显示帧率和控制点数量"""
        self.canvas.create_text(15, 15, anchor='nw', text=f"FPS: {fps:.1f}", fill='#2c3e50', font=('Consolas', 14, 'bold'), tags="temp")
        self.canvas.create_text(WIDTH-120, 15, anchor='nw', text=f"控制点: {point_count}", fill='#2c3e50', font=('Consolas', 14, 'bold'), tags="temp")
        # 提示文字
        self.canvas.create_text(15, HEIGHT-25, anchor='nw', text="鼠标左键: 添加控制点", fill='#555', font=('Consolas', 11), tags="temp")
        self.canvas.create_text(15, HEIGHT-10, anchor='nw', text="键盘 C: 清空所有点", fill='#555', font=('Consolas', 11), tags="temp")
    
    def draw_hint(self):
        """当没有点或只有一个点时显示额外提示"""
        if len(self.points) == 0:
            self.canvas.create_text(WIDTH//2, HEIGHT//2, text="👆 单击鼠标左键添加控制点", fill='#7f8c8d', font=('Segoe UI', 18), tags="temp")
        elif len(self.points) == 1:
            self.canvas.create_text(WIDTH//2, HEIGHT//2+40, text="至少需要两个控制点才能生成曲线", fill='#c0392b', font=('Segoe UI', 14), tags="temp")
    
    def update_animation(self):
        """动画循环：清空临时元素，重新绘制所有图形，计算帧率"""
        # 删除所有带 "temp" 标签的图形 (实现快速重绘)
        self.canvas.delete("temp")
        
        # 绘制静态网格 (也可以不清除，但为了保持一致，使用temp标签每次重绘)
        self.draw_grid()
        
        # 绘制控制多边形
        self.draw_control_polygon(self.points)
        # 绘制贝塞尔曲线
        self.draw_bezier_curve(self.points)
        # 绘制控制点
        self.draw_control_points(self.points)
        # 绘制信息文字和提示
        self.draw_info(self.fps, len(self.points))
        self.draw_hint()
        
        # 计算帧率 (每秒更新一次显示，但计算每帧的瞬时值并平滑)
        self.frame_count += 1
        now = time.time()
        dt = now - self.last_time
        if dt >= 0.5:   # 每0.5秒更新一次FPS数值，避免闪烁
            self.fps = self.frame_count / dt
            self.frame_count = 0
            self.last_time = now
        
        # 设置下一次刷新 (大约 60 FPS，即 16ms 一帧)
        self.root.after(16, self.update_animation)

if __name__ == "__main__":
    root = tk.Tk()
    app = BezierApp(root)
    root.mainloop()