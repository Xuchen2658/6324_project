const { createApp, ref, computed, onMounted } = Vue;

const app = createApp({
    setup() {
        const username = ref(window.PAGE_DATA?.username || "");
        const language = ref(window.PAGE_DATA?.language || "zh");
        const items = ref([]);

        const messages = {
            zh: {
                recentDeleted: '最近删除',
                restore: '恢复',
                restoreConfirm: '确定恢复这件衣物吗？',
                restoreSuccess: '恢复成功',
                recentDeletedEmpty: '最近删除为空',
                viewWardrobe: '查看衣橱库',
                mainCategory: '主分类',
                filename: '文件名',
                addedTime: '删除时间'
            },
            en: {
                recentDeleted: 'Recently Deleted',
                restore: 'Restore',
                restoreConfirm: 'Are you sure to restore this item?',
                restoreSuccess: 'Restore success',
                recentDeletedEmpty: 'No recently deleted items',
                viewWardrobe: 'View Wardrobe',
                mainCategory: 'Main Category',
                filename: 'Filename',
                addedTime: 'Deleted Time'
            },
            es: {
                recentDeleted: 'Eliminados recientemente',
                restore: 'Restaurar',
                restoreConfirm: '¿Seguro que deseas restaurar esta prenda?',
                restoreSuccess: 'Restaurado correctamente',
                recentDeletedEmpty: 'No hay elementos eliminados recientemente',
                viewWardrobe: 'Ver armario',
                mainCategory: 'Categoría principal',
                filename: 'Nombre de archivo',
                addedTime: 'Hora de eliminación'
            },
            ja: {
                recentDeleted: '最近削除したアイテム',
                restore: '復元',
                restoreConfirm: 'この服を復元してもよろしいですか？',
                restoreSuccess: '復元しました',
                recentDeletedEmpty: '最近削除したアイテムはありません',
                viewWardrobe: 'クローゼットを見る',
                mainCategory: '主分類',
                filename: 'ファイル名',
                addedTime: '削除日時'
            },
            ko: {
                recentDeleted: '최근 삭제',
                restore: '복원',
                restoreConfirm: '이 옷을 복원하시겠습니까?',
                restoreSuccess: '복원되었습니다',
                recentDeletedEmpty: '최근 삭제한 항목이 없습니다',
                viewWardrobe: '옷장 보기',
                mainCategory: '주 카테고리',
                filename: '파일명',
                addedTime: '삭제 시간'
            }
        };

        const t = computed(() => messages[language.value] || messages.zh);

        const loadDeleted = async () => {
            try {
                const data = await getJSON('/api/recent_deleted');
                items.value = data.items || [];
            } catch (err) {
                alert(err.message);
            }
        };

        const restoreItem = async (id) => {
            if (!confirm(t.value.restoreConfirm)) return;

            try {
                const data = await postJSON(`/api/recent_deleted/${id}/restore`, {});
                alert(data.message || t.value.restoreSuccess);
                await loadDeleted();
            } catch (err) {
                alert(err.message);
            }
        };

        const goWardrobe = () => {
            window.location.href = '/wardrobe';
        };

        onMounted(loadDeleted);

        return {
            username,
            language,
            items,
            t,
            restoreItem,
            goWardrobe
        };
    }
});

app.config.compilerOptions.delimiters = ['[[', ']]'];
app.mount('#app');