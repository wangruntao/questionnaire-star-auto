<template>
    <el-container class="mx-auto max-w-80\% text-center">
        <el-header>
            <h1 class="text-xl font-bold">URL 分析器</h1>
            <div class="text-sm text-gray-500 ">访问量：{{ visitCount }} 排队人数：{{ wait_num }}</div>

        </el-header>

        <el-main>
            <!-- <el-input v-model="urlInput" placeholder="请输入URL" class="mb-5"></el-input> -->
            <el-input v-model="urlInput" placeholder="请输入有效的问卷星URL" class="mb-5 mt-5"
                :class="{ 'input-error': !isValidUrl }"></el-input>
            <p v-if="!isValidUrl" class="error-message">请输入有效的 URL。</p>

            <el-button @click="analyzeURL" :loading="isLoading" type="primary" class="mt-5">分析</el-button>

            <div v-if="isLoading">
                <el-spinner></el-spinner>
            </div>

            <el-card v-if="questions.length > 0" class="box-card mt-5">
                <div v-for="(question, qIndex) in questions" :key="qIndex">
                    <h3 class="mb-4 text-lg">{{ question.question }} ({{ question.type }})</h3>
                    <el-row :gutter="20" class="flex-wrap justify-center">
                        <el-col v-if="question.answer_count === 0" :span="24">
                            <el-input type="text" v-model="prob[qIndex]" placeholder="请输入文本" class="mb-2"></el-input>
                        </el-col>
                        <el-col v-else v-for="ansIndex in question.answer_count" :key="`${qIndex}-${ansIndex}`"
                            :span="8">
                            <div class="mb-2">
                                <span>{{ `答案 ${ansIndex}:` }}</span>
                                <el-input-number v-model="prob[qIndex][ansIndex - 1]" :min="0"></el-input-number>
                            </div>
                        </el-col>
                    </el-row>
                </div>
                <div class="flex-auto mt-10">
                    <el-input-number v-model="num" label="份数:" min="0" class="mr-2"></el-input-number>份
                    <el-button class="submit-btn" type="success" @click="handleSubmit">提交</el-button>
                </div>
            </el-card>

            <div v-else class="mt-5">
                <p class="text-sm text-gray-500">请提交一个URL以获取分析结果。</p>
            </div>
        </el-main>
    </el-container>
</template>

<script>
import axios from 'axios';
import { ElMessage } from 'element-plus';
export default {
    data() {
        return {
            urlInput: '',      // 绑定到输入框的数据
            questions: [],     // 从后端API接收的问题数据
            prob: {},          // 绑定概率比例
            isLoading: false, // 控制加载状态显示
            isValidUrl: true,  // 控制 URL 验证状态
            visitCount: 0,
            wait_num: 0, // 还剩问卷数量
            // wait_time: 0, //预计等待时间
            num: 50,
            flag: true
        };
    },
    methods: {
        fetchQueueStatus() {
            axios.get('api/get_num')
                .then(response => {
                    this.wj_num = response.data.wj_num;
                    this.wait_time = this.wj_num / 100 * 3;
                })
                .catch(error => {
                    console.error('Error fetching queue status:', error);
                });
        },

        recordVisit() {
            axios.get('api/record_visit') // 访问数量+1
                .then(response => {
                    if (response.data.success) {
                        console.log("Visit recorded successfully.");
                    }
                })
                .catch(error => {
                    console.error("Failed to record visit:", error);
                });
        },
        fetchVisits() {
            axios.get('api/get_visits') // 获取访问量
                .then((response) => {
                    this.visitCount = response.data.visits;
                })
                .catch((error) => {
                    console.error('Failed to fetch visits', error);
                });

        },
        validateUrl(url) {
            // 简单的正则表达式，用于检查 URL 是否以 "https://www.wjx.cn/vm/" 开头
            const pattern = /^https:\/\/www\.wjx\.cn\/vm\//;
            return pattern.test(url);
        }
        ,
        handleSubmit() {
            if (this.flag) {
                const preparedProb = this.prepareProbData();
                const submission = {
                    task_list: {
                        num: this.num,
                        prob: preparedProb,
                        url: this.urlInput
                    }
                };
                this.flag = false
                axios.post('api/update_task_list', submission)
                    .then(response => {
                        ElMessage({
                            message: '提交成功!',
                            type: 'success',
                            duration: 3000
                        });
                        console.log('Submission successful', response.data);
                    })
                    .catch(error => {
                        ElMessage({
                            message: '提交失败: ' + error.message,
                            type: 'error',
                            duration: 3000
                        });
                        console.error('Submission failed', error);
                    });
            } else {
                ElMessage({
                    message: '请勿重复提交任务',
                    type: 'warning',
                    duration: 3000
                });
            }

        },
        analyzeURL() {
            if (!this.validateUrl(this.urlInput)) {
                this.isValidUrl = false;
                return; // 退出函数，不执行后续的分析
            }
            this.isValidUrl = true;

            this.isLoading = true;
            axios.post('api/analyze', { url: this.urlInput })
                .then(response => {
                    this.questions = response.data;
                    this.initProb();
                    console.log('Success:', response.data);
                })
                .catch(error => {
                    console.error('Error:', error);
                    this.questions = [];
                })
                .finally(() => {
                    this.isLoading = false;
                });
        },
        initProb() {
            this.prob = {}; // Reset prob object
            this.questions.forEach((question, qIndex) => {
                // 为每个问题初始化对应的答案概率或文本
                if (question.answer_count === 0) {
                    this.prob[qIndex] = ''; // 文本输入
                } else {
                    this.prob[qIndex] = new Array(question.answer_count).fill(1); // 答案概率
                }
            });
        },
        getWaitNum() {
            axios.get('api/get_wait_num').then(response => {
                console.log(response)
                this.wait_num = response.data.wait
            })
        },
        prepareProbData() {
            const probData = {};
            Object.keys(this.prob).forEach((qIndex) => {
                if (typeof this.prob[qIndex] === 'string') {
                    probData[qIndex] = this.prob[qIndex].split('；').map(x => x.trim());
                } else {
                    probData[qIndex] = this.prob[qIndex];
                }
            });
            return probData;
        },
    },
    mounted() {
        this.getWaitNum();
        this.fetchVisits();
        this.recordVisit();
        this.fetchQueueStatus();
        setInterval(this.fetchVisits, 10000); // 每10秒刷新一次访问量
        setInterval(this.fetchQueueStatus, 10000);
    },

};
</script>
<style>
.error-message {
    color: red;
    font-size: 0.875em;
    /* 使用相对小一点的字体大小 */
    margin-top: 5px;
}
.input-error {
    border-color: red;
    /* 输入框边框颜色标红 */
}
</style>
