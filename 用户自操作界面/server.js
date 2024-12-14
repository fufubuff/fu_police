const express = require("express");
const bodyParser = require("body-parser");
const cors = require("cors");
const { Pool } = require('pg');
const multer = require('multer');
const path = require('path');
const base64url = require('base64url');
const crypto = require('crypto');
const WebSocket = require('ws');

const app = express();

// 配置跨域选项，这里允许所有来源访问（可根据实际需求调整更严格的配置）
const corsOptions = {
    origin: "*", // 注意这里要根据需要进行更细致的配置
};
app.use(cors(corsOptions));

// 解析JSON格式和URL-encoded格式的请求体数据
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// 创建数据库连接池
const pool = new Pool({
    host: '101.132.80.183',
    port: 5433,
    database: 'dbf72a0c3d7d054ef39b98488f2995d159zz',
    user: 'zzsthere',
    password: '20020925Aa'
});

// 使用 async/await 重构数据库连接和表创建逻辑
const createTables = async () => {
    try {
        const createTextsTableSQL = `
            CREATE TABLE IF NOT EXISTS texts (
                id SERIAL PRIMARY KEY,
                text_content TEXT
            );
        `;
        const createImagesTableSQL = `
            CREATE TABLE IF NOT EXISTS images (
                id SERIAL PRIMARY KEY,
                image_path VARCHAR(255)
            );
        `;
        await pool.query(createTextsTableSQL);
        console.log('texts表创建成功');

        await pool.query(createImagesTableSQL);
        console.log('images表创建成功');
    } catch (err) {
        console.error('创建表失败: ', err);
    }
};

// 调用 createTables 来初始化数据库
pool.connect()
  .then(() => {
        console.log('数据库连接成功');
        createTables();
    })
  .catch(err => {
        console.error('数据库连接失败: ', err);
    });

// 设置文件上传
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/');
    },
    filename: (req, file, cb) => {
        cb(null, file.fieldname + '-' + Date.now() + path.extname(file.originalname));
    }
});
const upload = multer({ storage: storage });

// 处理文本上传
app.post('/uploadText', async (req, res) => {
    const textContent = req.body.text;
    const sql = 'INSERT INTO texts (text_content) VALUES ($1) RETURNING id';
    try {
        await pool.query(sql, [textContent]);
        res.send('文本数据上传成功');
    } catch (err) {
        console.error('插入文本数据失败: ', err);
        res.status(500).send('插入文本数据失败');
    }
});

// 处理图片上传
app.post('/uploadImage', upload.single('image'), async (req, res) => {
    const imagePath = req.file.path;
    const sql = 'INSERT INTO images (image_path) VALUES ($1) RETURNING id';
    try {
        await pool.query(sql, [imagePath]);
        res.send('图片数据上传成功');
    } catch (err) {
        console.error('插入图片数据失败: ', err);
        res.status(500).send('插入图片数据失败');
    }
});



// 设置端口
const PORT = process.env.PORT || 9090;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}.`);
});