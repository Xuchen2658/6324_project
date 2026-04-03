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
                myWardrobe: '我的衣橱库',
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
                batchUpload: '批量上传',
                batchDelete: '批量删除',
                selectAll: '全选当前页',
                unselectAll: '取消全选',
                selectedCount: '已选数量',
                batchDeleteConfirm: '确定批量删除这些衣物吗？',
                batchDeleteFail: '批量删除失败',
                batchUploadDone: '批量上传完成',
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
                batchUpload: 'Batch Upload',
                batchDelete: 'Batch Delete',
                selectAll: 'Select All',
                unselectAll: 'Unselect All',
                selectedCount: 'Selected',
                batchDeleteConfirm: 'Are you sure to batch delete these clothes?',
                batchDeleteFail: 'Batch delete failed',
                batchUploadDone: 'Batch upload finished',
                recentDeleted: 'Recently Deleted'
            },
            es: {
                myWardrobe: 'Mi armario',
                currentUser: 'Usuario actual',
                backHome: 'Volver al inicio',
                logout: 'Cerrar sesión',
                search: 'Buscar',
                clear: 'Limpiar',
                searchPlaceholder: 'Buscar por categoría, por ejemplo hoodie / shirt / skirt',
                searchHint: 'Puedes buscar prendas del usuario actual por palabras clave de categoría.',
                totalItems: 'Cantidad mostrada',
                emptyWardrobe: 'El armario está vacío o no hay prendas que coincidan con los filtros.',
                confidence: 'Confianza',
                filename: 'Nombre de archivo',
                season: 'Temporada',
                thickness: 'Grosor',
                delete: 'Eliminar',
                deleteConfirm: '¿Seguro que deseas eliminar esta prenda?',
                deleteSuccess: 'Eliminado correctamente',
                deleteFail: 'Error al eliminar',
                sortNewest: 'Ordenar por más reciente',
                sortOldest: 'Ordenar por más antiguo',
                categoryFilter: 'Filtro por categoría',
                allCategories: 'Todas las categorías',
                mainCategory: 'Categoría principal',
                addedTime: 'Fecha de ingreso',
                batchUpload: 'Carga múltiple',
                batchDelete: 'Eliminar en lote',
                selectAll: 'Seleccionar todo',
                unselectAll: 'Cancelar selección',
                selectedCount: 'Seleccionados',
                batchDeleteConfirm: '¿Seguro que deseas eliminar estas prendas?',
                batchDeleteFail: 'Error al eliminar en lote',
                batchUploadDone: 'Carga múltiple finalizada',
                recentDeleted: 'Eliminados recientemente'
            },
            ja: {
                myWardrobe: 'マイクローゼット',
                currentUser: '現在のユーザー',
                backHome: 'ホームに戻る',
                logout: 'ログアウト',
                search: '検索',
                clear: 'クリア',
                searchPlaceholder: 'カテゴリで検索してください。例：hoodie / shirt / skirt',
                searchHint: '現在のアカウントのクローゼット内の服をカテゴリキーワードで検索できます。',
                totalItems: '表示件数',
                emptyWardrobe: 'クローゼットが空か、フィルター条件に一致する服がありません。',
                confidence: '信頼度',
                filename: 'ファイル名',
                season: '季節',
                thickness: '厚さ',
                delete: '削除',
                deleteConfirm: 'この服を削除してもよろしいですか？',
                deleteSuccess: '削除しました',
                deleteFail: '削除に失敗しました',
                sortNewest: '新しい順',
                sortOldest: '古い順',
                categoryFilter: 'カテゴリフィルター',
                allCategories: 'すべてのカテゴリ',
                mainCategory: '主分類',
                addedTime: '追加日時',
                batchUpload: '一括アップロード',
                batchDelete: '一括削除',
                selectAll: 'すべて選択',
                unselectAll: '選択解除',
                selectedCount: '選択数',
                batchDeleteConfirm: 'これらの服を一括削除してもよろしいですか？',
                batchDeleteFail: '一括削除に失敗しました',
                batchUploadDone: '一括アップロードが完了しました',
                recentDeleted: '最近削除したアイテム'
            },
            ko: {
                myWardrobe: '내 옷장',
                currentUser: '현재 사용자',
                backHome: '홈으로 돌아가기',
                logout: '로그아웃',
                search: '검색',
                clear: '지우기',
                searchPlaceholder: '카테고리로 검색하세요. 예: hoodie / shirt / skirt',
                searchHint: '현재 계정의 옷장에서 카테고리 키워드로 검색할 수 있습니다.',
                totalItems: '표시된 개수',
                emptyWardrobe: '옷장이 비어 있거나 필터 조건에 맞는 옷이 없습니다.',
                confidence: '신뢰도',
                filename: '파일명',
                season: '계절',
                thickness: '두께',
                delete: '삭제',
                deleteConfirm: '이 옷을 삭제하시겠습니까?',
                deleteSuccess: '삭제되었습니다',
                deleteFail: '삭제 실패',
                sortNewest: '최신순 정렬',
                sortOldest: '오래된순 정렬',
                categoryFilter: '카테고리 필터',
                allCategories: '전체 카테고리',
                mainCategory: '주 카테고리',
                addedTime: '추가 시간',
                batchUpload: '일괄 업로드',
                batchDelete: '일괄 삭제',
                selectAll: '전체 선택',
                unselectAll: '전체 해제',
                selectedCount: '선택됨',
                batchDeleteConfirm: '이 옷들을 일괄 삭제하시겠습니까?',
                batchDeleteFail: '일괄 삭제 실패',
                batchUploadDone: '일괄 업로드 완료',
                recentDeleted: '최근 삭제'
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
                alert(`${t.value.batchUploadDone}: ${data.stored_count}`);
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