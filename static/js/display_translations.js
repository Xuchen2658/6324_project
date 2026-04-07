window.DisplayTranslator = (() => {
    const maps = {
        zh: {
            categories: {
                "Dress": "连衣裙",
                "Skirt": "半身裙",
                "Jeans": "牛仔裤",
                "Pants": "长裤",
                "Trousers": "长裤",
                "Shorts": "短裤",
                "Leggings": "打底裤",
                "Hoodie": "帽衫",
                "Coat": "外套",
                "Jacket": "夹克",
                "Blazer": "西装外套",
                "Cardigan": "开衫",
                "Sweater": "毛衣",
                "Shirt": "衬衫",
                "Blouse": "女式衬衫",
                "Top": "上衣",
                "T-Shirt": "短袖T恤",
                "Tank Top": "背心",
                "Pullover": "套头衫",
                "Sneakers": "运动鞋",
                "Shoes": "鞋子",
                "Boots": "靴子",
                "Heels": "高跟鞋",
                "Sandals": "凉鞋",
                "Hat": "帽子",
                "Cap": "鸭舌帽",
                "Beanie": "针织帽"
            },
            mainCategories: {
                "Tops": "上装",
                "Pants": "裤装",
                "Skirts": "裙装",
                "Outerwear": "外套",
                "Shoes": "鞋类",
                "Hats": "帽类",
                "Sweaters": "毛衣",
                "Short Sleeve": "短袖",
                "Long Sleeve": "长袖",
                "Others": "其他"
            },
            roles: {
                "Top": "上装",
                "Bottom": "下装",
                "Dress": "连衣裙",
                "Outerwear": "外套",
                "Shoes": "鞋子",
                "Hat": "帽子",
                "Other": "其他"
            },
            occasions: {
                "Daily": "日常",
                "Work": "通勤",
                "Sport": "运动",
                "Party": "聚会",
                "Formal": "正式",
                "Travel": "出行",
                "Home": "居家"
            },
            attrs: {
                "Long Sleeve": "长袖",
                "Short Sleeve": "短袖",
                "Sleeveless": "无袖",
                "Floral": "花纹",
                "Plaid": "格纹",
                "Striped": "条纹",
                "Solid": "纯色",
                "Pocket": "口袋",
                "Button": "纽扣",
                "Zipper": "拉链",
                "Knit": "针织",
                "Cotton": "棉",
                "Sateen": "缎面",
                "Denim": "牛仔布",
                "Lace": "蕾丝",
                "Belted": "系带",
                "Casual": "休闲",
                "Formal": "正式",
                "Soft": "柔软"
            },
            colors: {
                "red": "红色",
                "pink": "粉色",
                "orange": "橙色",
                "yellow": "黄色",
                "lime": "黄绿色",
                "green": "绿色",
                "cyan": "青色",
                "blue": "蓝色",
                "indigo": "靛蓝色",
                "purple": "紫色",
                "brown": "褐色",
                "beige": "米色",
                "white": "白色",
                "gray": "灰色",
                "black": "黑色",
                "unknown": "未知"
            },
            clothType: {
                "single": "单件",
                "two_piece": "上下装"
            }
        },
        en: {
            categories: {},
            mainCategories: {},
            roles: {},
            occasions: {},
            attrs: {},
            colors: {},
            clothType: {
                "single": "Single Piece",
                "two_piece": "Two Piece"
            }
        }
    };

    function prettyEnglish(text) {
        if (!text) return "Unknown";
        return String(text)
            .replace(/_/g, " ")
            .split(" ")
            .filter(Boolean)
            .map(w => w.charAt(0).toUpperCase() + w.slice(1))
            .join(" ");
    }

    function translateByMap(lang, section, value) {
        if (!value) return lang === "zh" ? "未知" : "Unknown";
        const sectionMap = maps[lang]?.[section] || {};
        return sectionMap[value] || value;
    }

    function translateColor(lang, color) {
        if (!color) return lang === "zh" ? "未知" : "Unknown";
        if (lang === "zh") {
            return maps.zh.colors[color.toLowerCase()] || color;
        }
        return prettyEnglish(color);
    }

    function displayCategory(lang, value) {
        if (!value) return lang === "zh" ? "未知" : "Unknown";
        if (lang === "zh") {
            return maps.zh.categories[value] || value;
        }
        return value;
    }

    function displayMainCategory(lang, value) {
        if (!value) return lang === "zh" ? "其他" : "Others";
        if (lang === "zh") {
            return maps.zh.mainCategories[value] || value;
        }
        return value;
    }

    function displayRole(lang, value) {
        if (!value) return lang === "zh" ? "其他" : "Other";
        if (lang === "zh") {
            return maps.zh.roles[value] || value;
        }
        return value;
    }

    function displayOccasion(lang, value) {
        if (!value) return "";
        if (lang === "zh") {
            return maps.zh.occasions[value] || value;
        }
        return value;
    }

    function displayAttr(lang, attr) {
        if (!attr) return lang === "zh" ? "未知" : "Unknown";

        const text = String(attr);

        if (text.toLowerCase().startsWith("color:")) {
            const raw = text.split(":")[1]?.trim() || "";
            const parts = raw.split("+").map(x => x.trim()).filter(Boolean);
            if (lang === "zh") {
                return `颜色: ${parts.map(c => translateColor(lang, c)).join(" + ")}`;
            }
            return `Color: ${parts.map(c => prettyEnglish(c)).join(" + ")}`;
        }

        if (text.toLowerCase().startsWith("cloth_type:")) {
            const raw = text.split(":")[1]?.trim() || "";
            if (lang === "zh") {
                return `穿搭类型: ${maps.zh.clothType[raw] || raw}`;
            }
            return `Cloth Type: ${maps.en.clothType[raw] || prettyEnglish(raw)}`;
        }

        if (lang === "zh") {
            return maps.zh.attrs[text] || text;
        }
        return text;
    }

    return {
        displayCategory,
        displayMainCategory,
        displayRole,
        displayOccasion,
        displayAttr
    };
})();