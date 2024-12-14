<template>
  <div id="app">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="logo-container">
        <img src="/static/logo.png" alt="网站logo" class="sidebar-logo" />
        <p class="logo-text">福卫兵</p>
      </div>
      <nav class="sidebar-nav">
        <ul>
          <li><router-link to="/" class="nav-link active">首页</router-link></li><!-- 当前页面高亮 --> 
          <li><router-link to="/data" class="nav-link">数据展示</router-link></li> <!-- 新增的数据展示按钮 -->
          <li><a href="#" class="nav-link">关于我们</a></li>
          <li><a href="#" class="nav-link">联系我们</a></li>
        </ul>
      </nav>
    </aside>

    <!-- 主体内容区 -->
    <div class="main-content">
      <!-- 文本和文件上传部分 -->
      <div class="text-upload-section">
        <textarea
          ref="textInput"
          placeholder="请输入要分析的文本内容"
          class="input-text"
        ></textarea>
        <div class="upload-section">
          <input type="file" id="fileInput" multiple accept="image/*, text/plain" />
          <button ref="analyzeButton" id="analyzeButton" class="upload-btn">上传并分析</button>
        </div>
      </div>

      <!-- 红色框 -->
      <div class="red-box">
        <div class="greeting-section">
          <div class="greeting-text">
            <p class="greeting-line-1">您好，福卫兵！</p>
            <p class="greeting-line-2">您的分析助手已上线。</p>
          </div>
          <img src="static/ai.png" alt="AI角色" class="ai-character-section" />
        </div>
        <!-- 分析结果展示区 -->
        <div class="result-section">
          <div class="analysis-box left">
            <h3>情感分析</h3>
            <canvas id="sentimentChart"></canvas>
          </div>
          <div class="analysis-box right">
            <h3>舆情分析结果</h3>
            <div id="publicOpinionResult" class="result-content">
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部栏 -->
    <footer class="footer">
      <img src="/static/logo.png" alt="网站logo" class="footer-logo" />
      <div class="footer-info">
        <p class="copyright">版权所有 &copy; 2024</p>
        <p class="contact">联系电话: 123456789</p>
      </div>
    </footer>
  </div>
</template>

<script>
import 'chart.js/auto';
import { Chart } from 'chart.js';
import axios from 'axios';
import { ref, onMounted, nextTick } from 'vue';

export default {
  setup() {
    const textInput = ref(null);
    const analyzeButton = ref(null);
    let isDrawing = false; // 标志位，用于检查是否正在绘制图表

    const navigateToDataDisplay = () => {
      window.location.href = '/data';
    };
    async function performSentimentAnalysis(text) {
      const url = "http://localhost:5000/sentiment-analysis";
      try {
        const response = await axios.post(url, { text });
        const resultData = response.data;
        console.log("前端接收到的后端返回数据:", resultData);
        return resultData; // 直接返回结果数据，不做格式验证，假设后端返回的数据格式是正确的
      } catch (error) {
        console.error('情感分析接口请求失败（后端接口）: ', error.response? error.response.data : error.message);
        return {
          anger: 0,
          disgust: 0,
          fear: 0,
          joy: 0,
          sadness: 0,
          surprise: 0,
          neutral: 0,
        };
      }
    }

        async function performPublicOpinionAnalysis(text, sentimentResult) {
          const url = "http://localhost:5000/public-opinion-analysis";
          try {
            const response = await axios.post(url, { text, sentimentResult });
            const resultData = response.data;
            console.log("前端接收到的舆情分析结果:", resultData);
            if (!resultData.error) {
              return resultData; // { text, sentimentResult, publicOpinionResult }
            } else {
              console.error('舆情分析失败:', resultData.error);
              return {
                text: text,
                sentimentResult: sentimentResult,
                publicOpinionResult: '舆情分析失败，请稍后重试。'
              };
            }
          } catch (error) {
            console.error('舆情分析接口请求失败（后端接口）: ', error.response ? error.response.data : error.message);
            return {
              text: text,
              sentimentResult: sentimentResult,
              publicOpinionResult: '舆情分析失败，请稍后重试。'
            };
          }
		  return publicOpinionResult;
        }

        function updatePublicOpinionResult(publicOpinionResult) {
            const publicOpinionResultElement = document.getElementById("publicOpinionResult");
            publicOpinionResultElement.innerHTML = `
              <p>${publicOpinionResult.publicOpinionResult}</p>
            `;
        }


    function drawSentimentChart(sentimentResult) {
      const canvasElement = document.getElementById('sentimentChart');
      if (!canvasElement) {
        console.error("canvas元素不存在，无法绘制图表");
        return;
      }
      const ctx = canvasElement.getContext('2d');
      if (isDrawing) {
        console.log("当前已有绘制操作正在进行，跳过本次绘制请求");
        return;
      }
      isDrawing = true;
      let chartInstance = Chart.getChart(ctx);
      if (chartInstance) {
        chartInstance.destroy();
      }
      const labels = Object.keys(sentimentResult);
      const data = Object.values(sentimentResult);
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: '情感占比',
            data: data,
            backgroundColor: [
              'rgba(255, 99, 132, 0.2)',
              'rgba(54, 162, 235, 0.2)',
              'rgba(255, 206, 86, 0.2)',
              'rgba(75, 192, 192, 0.2)',
              'rgba(153, 102, 255, 0.2)',
              'rgba(201, 203, 207, 0.2)',
              'rgba(255, 159, 64, 0.2)'
            ],
            borderColor: [
              'rgba(255, 99, 132, 1)',
              'rgba(54, 162, 235, 1)',
              'rgba(255, 206, 86, 1)',
              'rgba(75, 192, 192, 1)',
              'rgba(153, 102, 255, 1)',
              'rgba(201, 203, 207, 1)',
              'rgba(255, 159, 64, 1)'
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              type: 'category',
              display: true,
              title: {
                display: true,
                text: '情感类别'
              },
              ticks: {
                font: {
                  size: 12
                }
              }
            },
            y: {
              type: 'linear',
              beginAtZero: true,
              display: true,
              title: {
                display: true,
                text: '占比'
              },
              grid: {
                drawOnChartArea: false,
                drawTicks: true
              }
            }
          }
        }
      });
      isDrawing = false;
    }

    async function uploadTextToServer(text) {
      try {
        const response = await fetch('http://localhost:9090/uploadText', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ text })
        });
        const result = await response.text();
        console.log(result);
      } catch (error) {
        console.error('文本上传失败: ', error);
      }
    }

    async function uploadImageToServer(file) {
      const formData = new FormData();
      formData.append('image', file);
      try {
        const response = await fetch('http://localhost:9090/uploadImage', {
          method: 'POST',
          body: formData
        });
        const result = await response.text();
        console.log(result);
      } catch (error) {
        console.error('图片上传失败: ', error);
      }
    }

    onMounted(() => {
      nextTick(() => {
        const input = textInput.value;
        const button = analyzeButton.value;
    
        if (button) {
          button.addEventListener('click', async () => {
            try {
              // 1. 获取文本内容
              const textInputValue = input.value;
    
              // 2. 调用情感分析接口并等待结果
              const sentimentResult = await performSentimentAnalysis(textInputValue);
    
              // 3. 调用舆情分析接口，把文本和情感分析结果都传过去
              const publicOpinionData = await performPublicOpinionAnalysis(textInputValue, sentimentResult);
    
              // 4. 更新舆情分析展示区域
              updatePublicOpinionResult(publicOpinionData);
    
              // 5. 绘制情感分析图表
              drawSentimentChart(sentimentResult);
    
              // 6. 上传文件逻辑
              const fileInput = document.getElementById('fileInput');
              const files = fileInput.files;
              if (files.length > 0) {
                const file = files[0];
                if (file.type.startsWith('image/')) {
                  await uploadImageToServer(file);
                } else if (file.type === 'text/plain') {
                  const reader = new FileReader();
                  reader.onload = function (e) {
                    const textContent = e.target.result;
                    uploadTextToServer(textContent);
                  };
                  reader.readAsText(file);
                }
              }
    
            } catch (error) {
              console.error('分析流程出现错误:', error);
            }
          });
        } else {
          console.error('分析按钮元素未获取到，无法绑定点击事件，请检查元素是否正确渲染');
        }
      });
    });

    return {
      textInput,
      analyzeButton,
      navigateToDataDisplay
    };
  }
};
</script>

<style scoped>
/* 整体页面基础样式 */
body {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 0;
  background-color: #f2f2f2;
  color: #333;
  line-height: 1.6;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* 侧边栏样式 */
.sidebar {
  background-color: darkred; /* 保持深红色 */
  color: white;
  width: 220px; /* 调整侧边栏宽度 */
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  padding: 30px 0; /* 增加顶部和底部间距 */
  position: fixed;
  top: 0;
  left: 0;
  height: 100%;
  z-index: 1000;
}

.sidebar-logo {
  height: 60px; /* 增大 logo 高度 */
  width: auto;
  display: block;
}

.sidebar-nav {
  width: 100%;
}

.sidebar-nav ul {
  list-style-type: none;
  margin: 0;
  padding: 0;
}

.sidebar-nav ul li {
  text-align: center;
  margin-bottom: 25px; /* 增加列表项间距 */
}

.sidebar-nav ul li a.nav-link {
  color: white; /* 确保颜色为白色 */
  text-decoration: none;
  font-size: 18px;
  transition: color 0.3s ease, background-color 0.3s ease;
  padding: 10px 20px;
  border-radius: 5px;
  display: inline-block;
}

.sidebar-nav ul li a.nav-link.active,
.sidebar-nav ul li a.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.2); /* 保持浅灰色背景 */
  color: lightgray;
}

.logo-text {
  color: white;
  font-size: 18px;
  margin-top: 10px; /* 增加顶部间距 */
}

/* 主体内容区样式 */
.main-content {
  flex: 1;
  padding: 40px; /* 增加内边距 */
  border-radius: 10px; /* 增加圆角 */
  margin: 20px;
  background-color: white;
  margin-left: 240px; /* 调整主体内容区左边距 */
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 文本和文件上传部分样式 */
.text-upload-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 30px;
}

.input-text {
  width: 100%;
  width: 1000px;
  height: 180px;
  margin-bottom: 15px;
  padding: 15px;
  border: 1px solid #ccc;
  border-radius: 8px;
  resize: vertical;
  font-size: 17px;
  color: #333;
}

.upload-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.upload-btn {
  padding: 12px 25px;
  background-color: darkred; /* 保持深红色 */
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 8px;
  transition: background-color 0.3s ease;
  font-size: 14px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.upload-btn:hover {
  background-color: #0056b3; /* 保持蓝色悬停效果 */
}
/* 让舆情分析的文字变为黑色 */
.analysis-box.right .result-content p {
  color: #333 !important; /* 文字设为黑色 */
  /* 如果需要自动换行，可加上以下几条 */
  word-wrap: break-word;
  overflow-wrap: break-word;
  white-space: pre-wrap;  /* 用于保留换行符，如果不想保留换行改为 normal */
}

/* 限制舆情分析内容高度并产生滚动条（可选） */
.analysis-box.right .result-content {
  max-height: 200px; /* 你想要限制的高度 */
  overflow-y: auto;   /* 超出时出现纵向滚动条 */
  /* 如果想要始终显示滚动条，可改为 overflow-y: scroll; */
}
/* 红色框样式 */
.red-box {
  background-color: darkred; /* 保持深红色 */
  padding: 25px;
  border-radius: 10px;
  width: 80%;
  max-width: 1000px;
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  margin: auto;
  margin-top: 20px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);

  }

.greeting-section {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  margin-bottom: 20px;
}

.greeting-text {
  text-align: center;
}

.greeting-text p {
  font-size: 20px;
  margin: 0;
}

.greeting-line-1 {
  font-weight: bold;
  margin-bottom: 5px;
}

.greeting-line-2 {
  text-shadow: 0 0 2px rgba(0, 0, 0, 0.3);
}

.ai-character-section {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  box-shadow: 0 0 6px rgba(255, 255, 255, 0.3);
  margin-left: 20px;
}

.result-section {
  display: flex;
  justify-content: space-around;
  width: 100%;
  flex-wrap: nowrap;
  align-items: flex-start;
}

.analysis-box {
  width: 48%;
  padding: 15px;
  height: 300px;
  border-radius: 8px;
  box-shadow: 0 0 6px rgba(0, 0, 0, 0.3);
  background-color: white;
  margin-bottom: 20px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 0 1%;
  padding: 40px 15px; /* 增加内边距，特别是顶部 */
  margin: 0 1% 40px; /* 增加底部外边距 */
}

.analysis-box h3 {
  margin-top: 0;
  color: darkred; /* 保持深红色 */
  padding: 20px 15px; /* 增加内边距，特别是顶部 */
  margin: 0 1% 20px; /* 增加底部外边距 */
}
.result-content {
  flex: 1;                  /* 让内容自适应高度填充 */
  width: 100%;              /* 让内容宽度占满analysis-box */
  color: #333;              /* 深色文字 */
  line-height: 1.6;         /* 提高可读性 */
  /* padding: 10px 0;       // 如果需要更多留白，可以加上 */
}
/* 底部栏样式 */
.footer {
  text-align: center;
  margin-top: 20px;
  padding: 20px 0;
  background-color: #f2f2f2;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.footer-logo {
  height: 40px;
  width: 40px;
  margin-bottom: 10px;
}

.footer-info {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.copyright {
  margin-bottom: 5px;
  font-size: 14px;
}

.contact {
  color: #666;
  font-size: 14px;
}
</style>