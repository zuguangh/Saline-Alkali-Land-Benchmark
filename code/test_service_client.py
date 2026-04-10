import gradio as gr
import tempfile
import os
from test_plan_script import *


# 创建Gradio界面
with gr.Blocks(theme=gr.themes.Soft(), title="盐碱地治理智能系统") as demo:
    
    # 系统标题和介绍
    gr.Markdown("# 🌱 盐碱地治理智能问答系统")
    gr.Markdown("输入盐碱地土地信息，获取专业的治理措施推荐和综合治理方案")
    
    # 存储中间状态
    treatments_state = gr.State()
    plan_content_state = gr.State("")  # 存储方案内容
    
    with gr.Row():
        with gr.Column():
            # 土地信息输入
            gr.Markdown("## 土地信息输入")
            land_info_input = gr.Textbox(
                label="请输入盐碱地土地信息",
                placeholder="例如：pH值8.5，盐分含量0.4%，土壤类型为壤土，面积50亩...",
                lines=3
            )
            analyze_btn = gr.Button("分析土地信息", variant="primary")
            
            # 加载状态指示器
            analysis_status = gr.HTML(
                value="<div style='color: gray;'>等待分析...</div>",
                label="分析状态"
            )
            
            # 治理措施展示
            gr.Markdown("## 治理措施建议和成本信息")
            cost_output = gr.Markdown(  # 同时用于显示和存储成本信息
                label="治理措施和成本信息",
                value="请先输入土地信息并点击分析按钮..."
            )
            
            # 参考文献展示
            gr.Markdown("## 参考文献列表")
            references_output = gr.Markdown(
                label="相关参考文献",
                value="参考文献将在此显示..."
            )
            
        with gr.Column():
            # 预算输入
            gr.Markdown("## 成本预算")
            budget_input = gr.Number(
                label="请输入治理预算（元/亩）",
                value=1000,
                minimum=500
            )
            generate_plan_btn = gr.Button("生成治理方案", variant="primary")
            
            # 方案生成状态指示器
            plan_status = gr.HTML(
                value="<div style='color: gray;'>等待生成方案...</div>",
                label="方案生成状态"
            )
            
            # 治理方案展示
            gr.Markdown("## 综合治理方案")
            plan_output = gr.Markdown(
                label="治理方案详情",
                value="请先输入预算并点击生成方案按钮..."
            )
            
            # 下载按钮 - 修改：添加 file 参数用于动态更新
            download_btn = gr.DownloadButton(
                "下载治理方案 (MD格式)",
                visible=False,
                variant="secondary"
            )
            
    
    # 事件处理函数
    def process_land_info(land_info):
        """处理土地信息分析"""
        if not land_info.strip():
            return (
                None,  # treatments_state
                "请输入有效的土地信息",  # cost_output (显示)
                "请输入有效的土地信息",  # references_output
                "<div style='color: red;'>错误：请输入有效的土地信息</div>"  # analysis_status
            )
        
        # 更新状态为运行中
        status_html = "<div style='color: orange;'>🔄 分析中，请稍候...</div>"
        
        try:
            # 调用后端接口分析土地信息
            treatments, cost, references = generate_treatments(land_info)
            
            # 更新状态为完成
            status_html = "<div style='color: green;'>✅ 分析完成</div>"
            
            return treatments, cost, references, status_html
        except Exception as e:
            # 更新状态为错误
            error_html = f"<div style='color: red;'>❌ 分析出错: {str(e)}</div>"
            return None, f"分析过程中出现错误: {str(e)}", "", error_html
    
    def process_budget(treatments, cost_info, budget):
        """处理预算并生成方案"""
        if budget <= 0:
            return "请输入有效的预算金额", "", "<div style='color: red;'>错误：请输入有效的预算金额</div>", gr.update(visible=False)
        
        # 更新状态为运行中
        status_html = "<div style='color: orange;'>🔄 生成方案中，请稍候...</div>"
        
        try:
            # 调用后端接口生成方案
            plan = generate_plan(treatments, cost_info, budget)
            
            # 更新状态为完成
            status_html = "<div style='color: green;'>✅ 方案生成完成</div>"
            
            # 创建临时文件用于下载
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
                f.write(plan)
                temp_file_path = f.name
            
            return plan, temp_file_path, status_html, gr.update(visible=True)
        except Exception as e:
            # 更新状态为错误
            error_html = f"<div style='color: red;'>❌ 方案生成出错: {str(e)}</div>"
            return f"方案生成过程中出现错误: {str(e)}", "", error_html, gr.update(visible=False)
    
    # 删除原来的 create_download_file 函数
    
    # 绑定事件
    analyze_btn.click(
        fn=process_land_info,
        inputs=[land_info_input],
        outputs=[ 
            treatments_state,      # 存储治理措施数据
            cost_output,           # 显示并传递成本信息
            references_output,     # 显示参考文献
            analysis_status        # 显示分析状态
        ]
    )
    
    generate_plan_btn.click(
        fn=process_budget,
        inputs=[treatments_state, cost_output, budget_input],
        outputs=[
            plan_output,           # 显示治理方案
            download_btn,          # 直接更新下载按钮的文件路径
            plan_status,           # 显示方案生成状态
            download_btn           # 下载按钮可见性
        ]
    )


if __name__ == "__main__":
    # 启动应用
    demo.launch(
        server_name="0.0.0.0",
        share=False,
        show_error=True
    )