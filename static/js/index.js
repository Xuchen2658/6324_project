const { createApp, ref, computed, onMounted } = Vue;

createApp({
    delimiters: ['[[', ']]'],
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

        const messages = {
            zh: {
                currentUser: '当前用户',
                viewWardrobe: '查看衣橱库',
                logout: '退出',
                todayWeather: '今日天气',
                refreshWeather: '刷新天气',
                city: '城市',
                temperature: '当前温度',
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
                recentDeleted: '最近删除'
                changeLanguage: '更换语言',
                cityLabel: '城市',
            },
            en: {
                currentUser: 'Current User',
                viewWardrobe: 'View Wardrobe',
                logout: 'Logout',
                todayWeather: "Today's Weather",
                refreshWeather: 'Refresh Weather',
                city: 'City',
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
                recentDeleted: 'Recently Deleted'
                changeLanguage: 'Language',
                cityLabel: 'City',
            },
            es: {
                currentUser: 'Usuario actual',
                viewWardrobe: 'Ver armario',
                logout: 'Cerrar sesión',
                todayWeather: 'Clima de hoy',
                refreshWeather: 'Actualizar clima',
                city: 'Ciudad',
                temperature: 'Temperatura',
                feelsLike: 'Sensación térmica',
                tempMax: 'Temperatura máxima',
                tempMin: 'Temperatura mínima',
                rainProb: 'Probabilidad de lluvia',
                noWeather: 'No hay información meteorológica',
                todayRecommendedClothes: 'Ropa recomendada para hoy',
                score: 'Puntuación',
                noTodayRecommendation: 'No hay ropa recomendada para hoy',
                searchByCategory: 'Buscar ropa por categoría',
                searchPlaceholder: 'Introduce una categoría, por ejemplo hoodie / shirt / skirt',
                search: 'Buscar',
                noSearchResult: 'No se encontró ropa de esta categoría',
                storeUpload: 'Subir al armario',
                storeUploadDesc: 'La imagen se guardará en el armario del usuario actual y participará en búsquedas futuras.',
                uploadAndStore: 'Subir y guardar',
                recognitionResult: 'Resultado del reconocimiento',
                category: 'Categoría',
                confidence: 'Confianza',
                season: 'Temporada',
                thickness: 'Grosor',
                mostSimilarAfterStore: 'Prendas más similares después de guardar',
                similarity: 'Similitud',
                findSimilar: 'Buscar similares',
                findSimilarDesc: 'Sube una imagen sin guardarla y busca las prendas más similares en el armario actual.',
                searchOnly: 'Buscar similares',
                queryRecognition: 'Resultado de la imagen consultada',
                wardrobeSimilarItems: 'Prendas similares en el armario',
                noSimilarInWardrobe: 'El armario está vacío o no hay prendas comparables.',
                batchUpload: 'Carga múltiple',
                batchUploadDone: 'Carga múltiple finalizada',
                recentDeleted: 'Eliminados recientemente'
                changeLanguage: 'Idioma',
                cityLabel: 'Ciudad',
            },
            ja: {
                currentUser: '現在のユーザー',
                viewWardrobe: 'クローゼットを見る',
                logout: 'ログアウト',
                todayWeather: '今日の天気',
                refreshWeather: '天気を更新',
                city: '都市',
                temperature: '現在の気温',
                feelsLike: '体感温度',
                tempMax: '最高気温',
                tempMin: '最低気温',
                rainProb: '降水確率',
                noWeather: '天気情報が取得できません',
                todayRecommendedClothes: '今日おすすめの服',
                score: 'スコア',
                noTodayRecommendation: '今日のおすすめ衣類はありません',
                searchByCategory: 'カテゴリで服を検索',
                searchPlaceholder: 'カテゴリを入力してください。例：hoodie / shirt / skirt',
                search: '検索',
                noSearchResult: 'このカテゴリの服は見つかりませんでした',
                storeUpload: 'クローゼットに保存',
                storeUploadDesc: 'アップロード後、現在のアカウントのクローゼットに保存され、今後の類似検索に使用されます。',
                uploadAndStore: 'アップロードして保存',
                recognitionResult: '認識結果',
                category: 'カテゴリ',
                confidence: '信頼度',
                season: '季節',
                thickness: '厚さ',
                mostSimilarAfterStore: '保存後に最も類似した服',
                similarity: '類似度',
                findSimilar: '類似を探す',
                findSimilarDesc: '画像を保存せずにアップロードし、現在のクローゼット内で最も似た服を検索します。',
                searchOnly: '類似を探す',
                queryRecognition: '検索画像の認識結果',
                wardrobeSimilarItems: 'クローゼット内の類似服',
                noSimilarInWardrobe: 'クローゼットが空か、比較できる服がありません。',
                batchUpload: '一括アップロード',
                batchUploadDone: '一括アップロードが完了しました',
                recentDeleted: '最近削除したアイテム'
                changeLanguage: '言語',
                cityLabel: '都市',
            },
            ko: {
                currentUser: '현재 사용자',
                viewWardrobe: '옷장 보기',
                logout: '로그아웃',
                todayWeather: '오늘의 날씨',
                refreshWeather: '날씨 새로고침',
                city: '도시',
                temperature: '현재 기온',
                feelsLike: '체감 온도',
                tempMax: '최고 기온',
                tempMin: '최저 기온',
                rainProb: '강수 확률',
                noWeather: '날씨 정보를 불러올 수 없습니다',
                todayRecommendedClothes: '오늘 입기 좋은 옷',
                score: '점수',
                noTodayRecommendation: '오늘 추천할 옷이 없습니다',
                searchByCategory: '카테고리로 옷 검색',
                searchPlaceholder: '카테고리를 입력하세요. 예: hoodie / shirt / skirt',
                search: '검색',
                noSearchResult: '해당 카테고리의 옷을 찾지 못했습니다',
                storeUpload: '옷장에 저장',
                storeUploadDesc: '업로드한 이미지는 현재 계정의 옷장에 저장되며 이후 유사 검색에 사용됩니다.',
                uploadAndStore: '업로드 후 저장',
                recognitionResult: '인식 결과',
                category: '카테고리',
                confidence: '신뢰도',
                season: '계절',
                thickness: '두께',
                mostSimilarAfterStore: '저장 후 가장 유사한 옷',
                similarity: '유사도',
                findSimilar: '유사 항목 찾기',
                findSimilarDesc: '이미지를 저장하지 않고 업로드하여 현재 옷장에서 가장 비슷한 옷을 찾습니다.',
                searchOnly: '유사 항목 찾기',
                queryRecognition: '조회 이미지 인식 결과',
                wardrobeSimilarItems: '옷장 내 유사한 옷',
                noSimilarInWardrobe: '옷장이 비어 있거나 비교 가능한 옷이 없습니다.',
                batchUpload: '일괄 업로드',
                batchUploadDone: '일괄 업로드 완료',
                recentDeleted: '최근 삭제'
                changeLanguage: '언어',
                cityLabel: '도시',
            }
        };

        const t = computed(() => messages[language.value] || messages.zh);

        const loadDashboard = async () => {
            try {
                const data = await getJSON(`/api/dashboard?city=${encodeURIComponent(city.value)}`);
                dashboard.value = data || {};
                cityOptions.value = data.city_options || [];
                if (data.city) city.value = data.city;
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
            changeLanguage,
            loadDashboard,
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
}).mount('#app');