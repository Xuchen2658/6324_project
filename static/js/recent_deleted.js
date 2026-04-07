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
                viewWardrobe: '查看衣橱',
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
            }
        };

        const t = computed(() => messages[language.value] || messages.zh);

        const displayCategory = (value) => window.DisplayTranslator.displayCategory(language.value, value);
        const displayMainCategory = (value) => window.DisplayTranslator.displayMainCategory(language.value, value);
        const displayAttr = (value) => window.DisplayTranslator.displayAttr(language.value, value);

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
            goWardrobe,
            displayCategory,
            displayMainCategory,
            displayAttr
        };
    }
});

app.config.compilerOptions.delimiters = ['[[', ']]'];
app.mount('#app');