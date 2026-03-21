<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  close: []
}>()

function handleOverlayClick(e: MouseEvent) {
  if (e.target === e.currentTarget) {
    emit('close')
  }
}
</script>

<template>
  <Teleport to="body">
    <div v-if="visible" class="dialog-overlay" @click="handleOverlayClick">
      <div class="dialog">
        <div class="dialog-header">
          <div class="header-left">
            <span class="dialog-icon">📖</span>
            <span class="dialog-title">系统使用指南</span>
            <span class="badge">GUIDE</span>
          </div>
          <button class="close-btn" @click="emit('close')">×</button>
        </div>
        
        <div class="dialog-body guide-content">
          <div class="guide-scrollable">
            <h2>一、工具简介</h2>
            <div class="intro-card">
              <p><strong>AI 国际航班搜索助理</strong> 是一款基于大语言模型驱动的智能交互演示工具。它打破了传统复杂的查询表单，让您通过最自然的“大白话”聊天来探索全球航线报价。</p>
              <div class="intro-tags">
                <span class="tag">🤖 语义理解</span>
                <span class="tag">🧪 测试造数</span>
                <span class="tag">💬 会话记忆</span>
              </div>
            </div>

            <hr class="divider">

            <h2>二、实用功能亮点</h2>
            
            <div class="feature-card">
              <h3>🗣️ “口语化”机票搜索</h3>
              <p>支持输入热门城市名称（如上海、香港）或机场三字码（如PVG、HKG）。<br>
              支持提问相对日期词汇，如“明天”、“下周五”、“国庆节”，无需反复点选日历。</p>
            </div>

            <div class="feature-card">
              <h3>👥 精确的客群与舱位过滤</h3>
              <p>支持一句话带入组合结构，如“2个大人，1个小孩，要经济舱”。系统将自动为您获取对应票价和算价加总。系统能识别“头等舱”、“商务舱”等直滤要求。</p>
            </div>

            <div class="feature-card">
              <h3>🛡️ Mock 数据兜底演示</h3>
              <p>当您指定诸如“微信小程序”等过于严苛的长尾渠道或非常见航线导致无数据时，系统不会白屏报错，而是自动展示具有 `[MOCK]` 标签的自建假航班，确保界面与渲染流可测试。</p>
            </div>

            <div class="feature-card">
              <h3>💬 友好的追问与澄清卡片</h3>
              <p>当您信息提供不全（如只说“去北京”），系统会温柔弹出澄清卡片追问缺少的“出发地”和“日期”，补充后即可接续执行。</p>
            </div>

            <hr class="divider">

            <h2>二、操作演示语句</h2>
            <ul class="scenario-list">
              <li>
                <strong>🎯 场景 A（一步到位）</strong><br>
                <code>“明天早上上海飞东京，2个大人1个小孩，头等舱”</code>
              </li>
              <li>
                <strong>🎯 场景 B（触发追问，防呆测试）</strong><br>
                <code>“明晚去首尔的特价票”</code>
              </li>
              <li>
                <strong>🎯 场景 C（冷僻渠道，触发 Mock 兜底）</strong><br>
                <code>“下周二北京飞悉尼的微信小程序专属便宜班”</code>
              </li>
              <li>
                <strong>🎯 场景 D（黑话转码，精准过滤）</strong><br>
                <code>“PVG 到 ICN，不要经停，只要韩亚航空”</code>
              </li>
              <li>
                <strong>🎯 场景 E（节假日映射与多客逻辑）</strong><br>
                <code>“今年国庆节从广州去曼谷，两大一小”</code>
              </li>
              <li>
                <strong>🎯 场景 F（基于上下文追问补全）</strong><br>
                <code>搜完某班后回复：“帮我改到下周五” 或 “换成商务舱呢？”</code>
              </li>
            </ul>

            <hr class="divider">

            <h2>三、测试造数进阶指南（数据工厂）</h2>
            <div class="feature-card mock-focus">
              <h3>🛠️ 极端多段中转排版测试</h3>
              <p>对于罕见航线直接口头捏造数据测试前端卡片折叠与排版：<br>
              <code>“查一下 MU11/MU22/MU33 从上海去巴黎的单程，经曼谷和迪拜中转”</code><br>
              （或者说“转两次机，城市随便”，系统会自动补齐全航段 Mock）。</p>
            </div>

            <div class="feature-card mock-focus">
              <h3>🛠️ 极端多客报价边界校验</h3>
              <p>检测超大金额算价准确性及票种分列明细堆叠时的折行样式：<br>
              <code>“明天北京去洛杉矶，9个大人，9个小孩，2个婴儿，要头等舱”</code><br>
              底层算法将精准生成各种人群的折扣乘数及相加重叠后的完整 JSON。</p>
            </div>

            <div class="feature-card mock-focus">
              <h3>🛠️ 超级往返多段中转拦截</h3>
              <p>一次性生成去程+回程共达6段子航班的庞大数据块，测试极限渲染：<br>
              <code>“下周去巴黎的往返，来回都要转两次机”</code></p>
            </div>

            <div class="feature-card mock-focus">
              <h3>🛠️ 渠道透传与单航班精确定向</h3>
              <p>测试单一条目展示与定制化代理渠道回显标签：<br>
              <code>“只看明天 MU5101 的微信特惠渠道”</code></p>
            </div>

            <div class="test-note">
              <p><strong>💡 重要备注：</strong></p>
              <ul>
                <li>正常查询到的数据可以走下单业务流。</li>
                <li>Mock 用于极速造数测试，不受资源及网关过滤限制，暂不支持下单。</li>
              </ul>
            </div>
          </div>
        </div>
        
        <div class="dialog-footer">
          <button class="close-btn-secondary" @click="emit('close')">我知道了</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.dialog {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 700px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.dialog-icon {
  font-size: 20px;
}

.dialog-title {
  font-size: 16px;
  font-weight: 600;
}

.badge {
  font-size: 10px;
  padding: 2px 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  font-weight: 500;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  font-size: 20px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.dialog-body {
  flex: 1;
  overflow: hidden;
  padding: 0;
  background: #fdfdfd;
}

.guide-scrollable {
  max-height: calc(85vh - 130px);
  overflow-y: auto;
  padding: 24px;
  color: #333;
  line-height: 1.6;
}

/* 滚动条美化 */
.guide-scrollable::-webkit-scrollbar {
  width: 8px;
}
.guide-scrollable::-webkit-scrollbar-track {
  background: #f1f1f1;
}
.guide-scrollable::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 4px;
}
.guide-scrollable::-webkit-scrollbar-thumb:hover {
  background: #999;
}

.guide-scrollable h2 {
  font-size: 18px;
  color: #667eea;
  margin-bottom: 16px;
  font-weight: 700;
}

.feature-card {
  background: rgba(102, 126, 234, 0.05); /* very light blue/purple */
  border-left: 4px solid #667eea;
  padding: 12px 16px;
  margin-bottom: 16px;
  border-radius: 0 8px 8px 0;
}

.feature-card h3 {
  font-size: 15px;
  margin-bottom: 8px;
  color: #5a67d8;
}

.feature-card p {
  font-size: 14px;
  color: #374151;
  margin: 0;
}

.feature-card.mock-focus {
  background: #fdf4ff;
  border-left: 4px solid #c026d3;
}

.feature-card.mock-focus h3 {
  color: #86198f;
}

.feature-card.mock-focus code {
  background: #fdf2f8;
  color: #be185d;
  font-family: inherit;
  font-size: 13px;
  padding: 2px 6px;
  border-radius: 4px;
}

.divider {
  border: 0;
  height: 1px;
  background: #e5e7eb;
  margin: 24px 0;
}

.scenario-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.scenario-list li {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  padding: 12px 16px;
  margin-bottom: 12px;
  border-radius: 8px;
}

.scenario-list li strong {
  display: inline-block;
  margin-bottom: 6px;
  color: #111827;
}

.scenario-list li code {
  background: #f3f4f6;
  padding: 4px 8px;
  border-radius: 4px;
  color: #4b5563;
  font-family: inherit;
  font-size: 13px;
  display: block;
}

/* 新增工具简介卡片样式 */
.intro-card {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 16px;
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.intro-card p {
  font-size: 15px;
  color: #4b5563;
  line-height: 1.7;
  margin-bottom: 15px;
}

.intro-tags {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.intro-tags .tag {
  background: white;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  color: #667eea;
  font-weight: 500;
  box-shadow: 0 2px 6px rgba(102, 126, 234, 0.1);
}

.test-note {
  margin-top: 24px;
  padding: 16px;
  background: #fff7ed;
  border-left: 4px solid #f97316;
  border-radius: 4px;
}

.test-note p {
  color: #c2410c;
  font-weight: 600;
  margin-bottom: 8px;
  font-size: 14px;
}

.test-note ul {
  margin: 0;
  padding-left: 20px;
}

.test-note li {
  color: #9a3412;
  font-size: 13px;
  margin-bottom: 4px;
  line-height: 1.5;
}

.dialog-footer {
  padding: 16px 20px;
  background: #f8f9fa;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  border-radius: 0 0 16px 16px;
  flex-shrink: 0;
}

.close-btn-secondary {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  background: #667eea;
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.close-btn-secondary:hover {
  background: #5a67d8;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}
</style>
