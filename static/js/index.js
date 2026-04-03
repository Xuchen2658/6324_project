const { createApp, ref, computed, onMounted } = Vue;

const app = createApp({
    setup() {
        const username = ref(window.PAGE_DATA?.username || "");
        const language = ref(window.PAGE_DATA?.language || "zh");

        const city = ref('Arlington');
        const cityOptions = ref([]);
        const dashboard = ref({});
        const searchQuery = ref('');
        const searchResults = ref([]);
        const searchPerformed = ref(false);

        const storeFile = ref(null);
        const storeFiles = ref([]);
        const storePreview = ref('');
        const storeResult = ref(null);

        const searchFile = ref(null);
        const searchPreview = ref('');
        const searchResult = ref(null);

        const selectedOccasion = ref("Daily");
        const occasionOptions = ref(["Daily", "Work", "Sport", "Party", "Formal", "Travel", "Home"]);
        const occasionItems = ref([]);
        const outfitRecommendations = ref([]);

        const messages = {
            zh: {
                currentUser: '当前用户',
                viewWardrobe: '查看衣橱库',
                logout: '退出',
                todayWeather: '今日天气',
                refreshWeather: '刷新天气',
                city: '城市',
                cityLabel: '城市',
                changeLanguage: '更换语言',
                feelsLike: '体感温度',
                tempMax: '最高温度',
                tempMin: '最低温度',
                rainProb: '降雨概率',
                noWeather: '未获取到天气信息',
                todayRecommendedClothes: '今日适合穿的衣服',
                score: '匹配分数',
                noTodayRecommendation: '当前衣橱库暂无今日推荐',
                searchByCategory: '按类别搜索衣服',
                searchPlaceholder: '输入类别，例如 hoodie / shirt / skirt',
                search: '搜索',
                noSearchResult: '没有找到该类别衣物',
                storeUpload: '入库上传',
                storeUploadDesc: '上传后保存到当前账号衣橱库，并参与后续相似检索。',
                uploadAndStore: '上传并入库',
                recognitionResult: '识别结果',
                category: '类别',
                confidence: '置信度',
                season: '季节',
                thickness: '厚度',
                temperature: '当前温度',
                mostSimilarAfterStore: '入库后最相似衣物',
                similarity: '相似度',
                findSimilar: '找相似',
                findSimilarDesc: '上传图片不入库，只在当前账号已有衣橱库中搜索最相似衣物。',
                searchOnly: '找相似',
                queryRecognition: '查询图识别结果',
                wardrobeSimilarItems: '库内相似衣物',
                noSimilarInWardrobe: '当前衣橱库为空，或没有可比较的衣物。',
                batchUpload: '批量上传',
                batchUploadDone: '批量上传完成',
                recentDeleted: '最近删除',
                occasion: '场合',
                occasionRecommend: '按场合推荐',
                smartOutfits: '智能搭配推荐',
                refreshOccasionRecommend: '获取推荐',
                noOccasionItems: '当前衣橱中没有适合该场合的单品推荐',
                noOutfits: '当前衣橱中暂时无法生成该场合的搭配',
                outfitScore: '搭配分数',
                reasons: '推荐理由'
            },
            en: {
                currentUser: 'Current User',
                viewWardrobe: 'View Wardrobe',
                logout: 'Logout',
                todayWeather: "Today's Weather",
                refreshWeather: 'Refresh Weather',
                city: 'City',
                cityLabel: 'City',
                changeLanguage: 'Language',
                temperature: 'Temperature',
                feelsLike: 'Feels Like',
                tempMax: 'Max Temperature',
                tempMin: 'Min Temperature',
                rainProb: 'Rain Probability',
                noWeather: 'Weather unavailable',
                todayRecommendedClothes: "Today's Recommended Clothes",
                score: 'Score',
                noTodayRecommendation: 'No recommended clothes for today',
                searchByCategory: 'Search Clothes by Category',
                searchPlaceholder: 'Enter category, e.g. hoodie / shirt / skirt',
                search: 'Search',
                noSearchResult: 'No clothes found in this category',
                storeUpload: 'Store Upload',
                storeUploadDesc: 'Upload and save to current user wardrobe for future similarity search.',
                uploadAndStore: 'Upload and Store',
                recognitionResult: 'Recognition Result',
                category: 'Category',
                confidence: 'Confidence',
                season: 'Season',
                thickness: 'Thickness',
                mostSimilarAfterStore: 'Most Similar After Storing',
                similarity: 'Similarity',
                findSimilar: 'Find Similar',
                findSimilarDesc: 'Upload an image without storing it, and search the most similar items in the current wardrobe.',
                searchOnly: 'Find Similar',
                queryRecognition: 'Query Recognition',
                wardrobeSimilarItems: 'Similar Items in Wardrobe',
                noSimilarInWardrobe: 'Wardrobe is empty or no comparable items found.',
                batchUpload: 'Batch Upload',
                batchUploadDone: 'Batch upload finished',
                recentDeleted: 'Recently Deleted',
                occasion: 'Occasion',
                occasionRecommend: 'Occasion Recommendations',
                smartOutfits: 'Smart Outfit Suggestions',
                refreshOccasionRecommend: 'Get Recommendations',
                noOccasionItems: 'No item recommendations for this occasion',
                noOutfits: 'No outfit combinations available for this occasion',
                outfitScore: 'Outfit Score',
                reasons: 'Reasons'
            }
        };

        const t = computed(() => messages[language.value] || messages.zh);

        const loadDashboard = async () => {
            try {
                const data = await getJSON(`/api/dashboard?city=${encodeURIComponent(city.value)}`);
                dashboard.value = data || {};
                cityOptions.value = data.city_options || [];
                occasionOptions.value = data.occasion_options || occasionOptions.value;
                if (data.city) city.value = data.city;
            } catch (err) {
                alert(err.message);
            }
        };

        const loadOccasionRecommendations = async () => {
            try {
                const itemData = await getJSON(
                    `/api/recommend_by_occasion?occasion=${encodeURIComponent(selectedOccasion.value)}&city=${encodeURIComponent(city.value)}`
                );
                occasionItems.value = itemData.recommended_items || [];

                const outfitData = await getJSON(
                    `/api/recommend_outfits?occasion=${encodeURIComponent(selectedOccasion.value)}&city=${encodeURIComponent(city.value)}`
                );
                outfitRecommendations.value = outfitData.outfits || [];
            } catch (err) {
                alert(err.message);
            }
        };

        const searchClothes = async () => {
            const q = searchQuery.value.trim();
            searchPerformed.value = true;
            if (!q) {
                searchResults.value = [];
                return;
            }

            try {
                const data = await getJSON(`/api/search_clothes?q=${encodeURIComponent(q)}`);
                searchResults.value = data.items || [];
            } catch (err) {
                alert(err.message);
            }
        };

        const changeLanguage = async () => {
            try {
                const data = await postJSON('/api/language', { language: language.value });
                language.value = data.language || language.value;
            } catch (err) {
                alert(err.message);
            }
        };

        const onStoreFileChange = (e) => {
            const files = Array.from(e.target.files || []);
            storeFiles.value = files;
            storeFile.value = files.length ? files[0] : null;
            storePreview.value = files.length ? URL.createObjectURL(files[0]) : '';
        };

        const onSearchFileChange = (e) => {
            const file = e.target.files[0];
            searchFile.value = file || null;
            searchPreview.value = file ? URL.createObjectURL(file) : '';
        };

        const uploadStore = async () => {
            if (!storeFile.value) {
                alert('Please choose an image');
                return;
            }

            try {
                const fd = new FormData();
                fd.append('file', storeFile.value);
                const data = await postForm('/upload_store', fd);
                storeResult.value = data;
                await loadDashboard();
                await loadOccasionRecommendations();
            } catch (err) {
                alert(err.message);
            }
        };

        const uploadStoreBatch = async () => {
            if (!storeFiles.value.length) {
                alert('Please choose files');
                return;
            }

            try {
                const fd = new FormData();
                storeFiles.value.forEach(file => fd.append('files', file));
                const data = await postForm('/upload_store_batch', fd);
                alert(`${t.value.batchUploadDone}: ${data.stored_count}`);
                await loadDashboard();
                await loadOccasionRecommendations();
            } catch (err) {
                alert(err.message);
            }
        };

        const searchSimilar = async () => {
            if (!searchFile.value) {
                alert('Please choose an image');
                return;
            }

            try {
                const fd = new FormData();
                fd.append('file', searchFile.value);
                const data = await postForm('/search_similar', fd);
                searchResult.value = data;
            } catch (err) {
                alert(err.message);
            }
        };

        const formatWeatherValue = (value, suffix = '') => {
            if (value === null || value === undefined || value === '') return 'N/A';
            return `${value}${suffix}`;
        };

        const goWardrobe = () => {
            window.location.href = '/wardrobe';
        };

        const goRecentDeleted = () => {
            window.location.href = '/recent_deleted';
        };

        const logout = () => {
            window.location.href = '/logout';
        };

        onMounted(async () => {
            await loadDashboard();
            await loadOccasionRecommendations();
        });

        return {
            username,
            language,
            t,
            city,
            cityOptions,
            dashboard,
            searchQuery,
            searchResults,
            searchPerformed,
            storePreview,
            storeResult,
            searchPreview,
            searchResult,
            selectedOccasion,
            occasionOptions,
            occasionItems,
            outfitRecommendations,
            changeLanguage,
            loadDashboard,
            loadOccasionRecommendations,
            searchClothes,
            onStoreFileChange,
            onSearchFileChange,
            uploadStore,
            uploadStoreBatch,
            searchSimilar,
            formatWeatherValue,
            goWardrobe,
            goRecentDeleted,
            logout
        };
    }
});

app.config.compilerOptions.delimiters = ['[[', ']]'];
app.mount('#app');