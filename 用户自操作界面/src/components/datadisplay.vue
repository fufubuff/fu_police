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
          <li><router-link to="/" class="nav-link">首页</router-link></li>
          <li><router-link to="/data" class="nav-link active">数据展示</router-link></li> <!-- 当前页面高亮 -->
          <li><a href="#" class="nav-link">关于我们</a></li>
          <li><a href="#" class="nav-link">联系我们</a></li>
        </ul>
      </nav>
    </aside>

    <!-- 主体内容区 -->
    <div class="main-content">
      <!-- 搜索框 -->
      <div class="search-section">
        <input
          type="text"
          v-model="searchQuery"
          @keyup.enter="searchData"
          placeholder="请输入关键词进行搜索"
          class="search-input"
        />
        <button @click="searchData" class="search-btn">搜索</button>
      </div>

      <!-- 搜索结果展示区 -->
      <div class="search-result-section">
        <div class="search-result-box">
          <h2>搜索结果</h2>
          <div v-if="noResultsVisible" class="no-results">
            <p>没有找到相关数据。</p>
          </div>
          <div v-else>
            <div v-for="(item, index) in searchResults" :key="index" class="search-item">
              <p><strong>微博内容:</strong> {{ item.展示内容 }}</p>
              <p><strong>发布时间:</strong> {{ item.发布时间 }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 舆情分析结果 -->
      <div class="red-box">
        <div class="greeting-section">
          <div class="greeting-text">
            <p class="greeting-line-1">您好，福卫兵！</p>
            <p class="greeting-line-2">您的分析助手已上线。</p>
          </div>
          <img src="static/ai.png" alt="AI角色" class="ai-character-section" />
        </div>
        <div class="result-section">
          <div class="analysis-box right">
            <h3>舆情分析结果</h3>
            <div id="publicOpinionResult" class="result-content">
              {{ analysisResult }}
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
import { ref } from 'vue';
import axios from 'axios';

export default {
  setup() {
    const searchQuery = ref('');
    const searchResults = ref([]);
    const noResultsVisible = ref(false);
    const analysisResult = ref('');
    const searchData = () => {
      const query = searchQuery.value.toLowerCase();
      if (query === '') {
        searchResults.value = [];
        return;
      }
        axios.get('http://localhost:5000/api/search-and-analyze', {
              params: {
                keyword: query
              }
            })
            .then(response => {
              // response.data应包含: { results: [...], analysis: "AI分析内容", extractedKeywords: "..." }
              const data = response.data;
              searchResults.value = data.results || [];
              analysisResult.value = data.analysis || '';
      
              if (searchResults.value.length === 0) {
                noResultsVisible.value = true;
              } else {
                noResultsVisible.value = false;
              }
            })
            .catch(error => {
              console.error(error);
              searchResults.value = [];
              noResultsVisible.value = true;
              analysisResult.value = 'AI分析失败或接口请求出错。';
            });
          };
      
          return {
            searchQuery,
            searchResults,
            noResultsVisible,
            analysisResult, // 返回给模板
            searchData
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

/* 搜索框和按钮样式 */
.search-section {
  width: 80%;
  max-width: 800px;
  display: flex;
  justifyContent: center;
  margin-bottom: 30px;
}

.search-input {
  width: 60%;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 16px;
}

.search-btn {
  padding: 12px 25px;
  margin-left: 10px;
  background-color: darkred; /* 保持深红色 */
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  font-size: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.search-btn:hover {
  background-color: #b71c1c; /* 更深的红色 */
}

/* 搜索结果展示区样式 */
.search-result-section {
  width: 80%;
  max-width: 1000px;
  margin-top: 20px;
  align-items: center;  
}

.search-result-box {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  width: 100%;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  color: #333;
}

.no-results {
  text-align: center;
  font-size: 16px;
  color: #555;
}

.search-item {
  margin-bottom: 10px;
}

.search-item p {
  margin: 0;
  font-size: 16px;
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
  margin: 20px auto; /* 垂直居中 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  color: white;
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
  justifyContent: space-around;
  width: 100%;
  flex-wrap: nowrap;
  align-items: flex-start;
}

.analysis-box {
  /* width: 48%; 这个可根据需要保留 */
  padding: 15px;
  /* height: 300px;           // 移除固定高度 */
  border-radius: 8px;
  box-shadow: 0 0 6px rgba(0, 0, 0, 0.3);
  background-color: white;
  margin-bottom: 20px;
  flex-grow: 1;

  /* 
   * 移除原先的居中对齐，这样标题自然会顶在最上方，
   * 内容也会顺着文档流来填充容器
   */
  display: flex;
  flex-direction: column;
  /* align-items: center; */
  /* justify-content: center; */

  margin: 0 1%; /* 保持水平间距 */
}

/* 调整标题与内容的间距，让布局更美观 */
.analysis-box h3 {
  margin-top: 0;
  margin-bottom: 10px; /* 给标题和内容留出一些间距 */
  color: darkred; /* 保持深红色 */
}

/* 如果需要让分析内容更好地填充容器，可以给内容单独做样式 */
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