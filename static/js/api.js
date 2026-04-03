async function getJSON(url) {
    const resp = await fetch(url);
    const data = await resp.json();
    if (!resp.ok) {
        throw new Error(data.error || "Request failed");
    }
    return data;
}

async function postJSON(url, body) {
    const resp = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(body)
    });

    const data = await resp.json();
    if (!resp.ok) {
        throw new Error(data.error || "Request failed");
    }
    return data;
}

async function deleteJSON(url) {
    const resp = await fetch(url, {
        method: "DELETE"
    });

    const data = await resp.json();
    if (!resp.ok) {
        throw new Error(data.error || "Request failed");
    }
    return data;
}

async function postForm(url, formData) {
    const resp = await fetch(url, {
        method: "POST",
        body: formData
    });

    const data = await resp.json();
    if (!resp.ok) {
        throw new Error(data.error || "Request failed");
    }
    return data;
}