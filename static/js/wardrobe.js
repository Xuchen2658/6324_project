const { createApp, ref, computed, onMounted } = Vue;

const app = createApp({
    setup() {
        const username = ref(window.PAGE_DATA?.username || "");
        const language = ref(window.PAGE_DATA?.language || "zh");

        const items = ref([]);
        const keyword = ref('');
        const searchMode = ref(false);
        const sortOrder = ref('newest');
        const selectedCategory = ref('All');
        const selectedIds = ref([]);
        const batchFiles = ref([]);

        const messages = {
            zh: {
                myWardrobe: '我的衣橱',
                currentUser: '当前用户',
                backHome: '返回主页',
                logout: '退出',
                search: '搜索',
                clear: '清空',
                searchPlaceholder: '输入类别搜索，例如 hoodie / shirt / skirt',
                searchHint: '可按类别关键字搜索当前账号衣橱中的衣物。',
                totalItems: '当前显示数量',
                emptyWardrobe: '当前衣橱库为空，或没有符合筛选条件的衣物。',
                confidence: '置信度',
                filename: '文件名',
                season: '季节',
                thickness: '厚度',
                delete: '删除',
                deleteConfirm: '确定删除这件衣物吗？',
                deleteSuccess: '删除成功',
                deleteFail: '删除失败',
                sortNewest: '按最新时间排序',
                sortOldest: '按最早时间排序',
                categoryFilter: '分类筛选',
                allCategories: '全部分类',
                mainCategory: '主分类',
                addedTime: '入库时间',
                submit: '提交',
                batchDelete: '批量删除',
                selectAll: '全选',
                unselectAll: '取消全选',
                selectedCount: '已选数量',
                batchDeleteConfirm: '确定批量删除这些衣物吗？',
                batchDeleteFail: '批量删除失败',
                uploadDone: '上传完成',
                recentDeleted: '最近删除'
            },
            en: {
                myWardrobe: 'My Wardrobe',
                currentUser: 'Current User',
                backHome: 'Back Home',
                logout: 'Logout',
                search: 'Search',
                clear: 'Clear',
                searchPlaceholder: 'Search by category, e.g. hoodie / shirt / skirt',
                searchHint: 'Search clothes in the current account wardrobe by category keywords.',
                totalItems: 'Displayed Items',
                emptyWardrobe: 'The wardrobe is empty or no items match the filters.',
                confidence: 'Confidence',
                filename: 'Filename',
                season: 'Season',
                thickness: 'Thickness',
                delete: 'Delete',
                deleteConfirm: 'Are you sure to delete this item?',
                deleteSuccess: 'Deleted successfully',
                deleteFail: 'Delete failed',
                sortNewest: 'Sort by newest',
                sortOldest: 'Sort by oldest',
                categoryFilter: 'Category Filter',
                allCategories: 'All Categories',
                mainCategory: 'Main Category',
                addedTime: 'Added Time',
                submit: 'Submit',
                batchDelete: 'Batch Delete',
                selectAll: 'Select All',
                unselectAll: 'Unselect All',
                selectedCount: 'Selected',
                batchDeleteConfirm: 'Are you sure to batch delete these clothes?',
                batchDeleteFail: 'Batch delete failed',
                uploadDone: 'Upload completed',
                recentDeleted: 'Recently Deleted'
            }
        };

        const t = computed(() => messages[language.value] || messages.zh);

        const categoryOptions = computed(() => {
            const set = new Set();
            items.value.forEach(item => {
                if (item.main_category) set.add(item.main_category);
            });
            return Array.from(set);
        });

        const filteredItems = computed(() => {
            let result = items.value;

            if (!searchMode.value) {
                const q = keyword.value.trim().toLowerCase();
                if (q) {
                    result = result.filter(item =>
                        (item.category_name || '').toLowerCase().includes(q)
                    );
                }
            }

            if (selectedCategory.value !== 'All') {
                result = result.filter(item => item.main_category === selectedCategory.value);
            }

            return result;
        });

        const allSelected = computed(() => {
            return filteredItems.value.length > 0 &&
                filteredItems.value.every(item => selectedIds.value.includes(item.id));
        });

        const loadItems = async () => {
            try {
                const data = await getJSON(`/api/wardrobe?sort=${encodeURIComponent(sortOrder.value)}`);
                items.value = data.items || [];
                searchMode.value = false;
                selectedIds.value = [];
            } catch (err) {
                alert(err.message);
            }
        };

        const searchRemote = async () => {
            const q = keyword.value.trim();
            if (!q) {
                await loadItems();
                return;
            }

            try {
                const data = await getJSON(`/api/search_clothes?q=${encodeURIComponent(q)}`);
                items.value = data.items || [];
                searchMode.value = true;
                selectedIds.value = [];
            } catch (err) {
                alert(err.message);
            }
        };

        const clearSearch = async () => {
            keyword.value = '';
            selectedCategory.value = 'All';
            await loadItems();
        };

        const changeLanguage = async () => {
            try {
                const data = await postJSON('/api/language', { language: language.value });
                language.value = data.language || language.value;
            } catch (err) {
                alert(err.message);
            }
        };

        const deleteItem = async (id) => {
            if (!confirm(t.value.deleteConfirm)) return;

            try {
                const data = await deleteJSON(`/api/clothes/${id}`);
                alert(data.message || t.value.deleteSuccess);
                await loadItems();
            } catch (err) {
                alert(err.message || t.value.deleteFail);
            }
        };

        const onBatchFileChange = (e) => {
            batchFiles.value = Array.from(e.target.files || []);
        };

        const uploadBatch = async () => {
            if (!batchFiles.value.length) {
                alert('Please choose files');
                return;
            }

            try {
                const fd = new FormData();
                batchFiles.value.forEach(file => fd.append('files', file));
                const data = await postForm('/upload_store_batch', fd);
                alert(`${t.value.uploadDone}: ${data.stored_count}`);
                batchFiles.value = [];
                await loadItems();
            } catch (err) {
                alert(err.message);
            }
        };

        const toggleSelectAll = () => {
            if (allSelected.value) {
                selectedIds.value = [];
            } else {
                selectedIds.value = filteredItems.value.map(item => item.id);
            }
        };

        const batchDelete = async () => {
            if (!selectedIds.value.length) return;
            if (!confirm(t.value.batchDeleteConfirm)) return;

            try {
                await postJSON('/api/clothes/batch_delete', { ids: selectedIds.value });
                selectedIds.value = [];
                await loadItems();
            } catch (err) {
                alert(err.message || t.value.batchDeleteFail);
            }
        };

        const goHome = () => {
            window.location.href = '/';
        };

        const goRecentDeleted = () => {
            window.location.href = '/recent_deleted';
        };

        const logout = () => {
            window.location.href = '/logout';
        };

        onMounted(async () => {
            await loadItems();
        });

        return {
            username,
            language,
            items,
            keyword,
            t,
            filteredItems,
            searchRemote,
            clearSearch,
            changeLanguage,
            deleteItem,
            goHome,
            goRecentDeleted,
            logout,
            sortOrder,
            selectedCategory,
            categoryOptions,
            loadItems,
            selectedIds,
            batchFiles,
            onBatchFileChange,
            uploadBatch,
            allSelected,
            toggleSelectAll,
            batchDelete
        };
    }
});

app.config.compilerOptions.delimiters = ['[[', ']]'];
app.mount('#app');