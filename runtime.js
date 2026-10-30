/* Runtime caches hold references only up to explicit budgets. Browser/GPU memory is separate. */
(() => {
    'use strict';
    const MiB = 1024 * 1024;
    class BudgetCache {
        constructor(limit, maxEntries = 256) {
            this.limit = limit; this.maxEntries = maxEntries;
            this.entries = new Map(); this.bytes = 0;
            this.hits = 0; this.misses = 0;
        }
        get(key) {
            const entry = this.entries.get(key);
            if (!entry) { this.misses++; return undefined; }
            this.hits++;
            this.entries.delete(key); this.entries.set(key, entry);
            return entry.value;
        }
        set(key, value, bytes) {
            this.delete(key);
            if (bytes > this.limit) return value;
            this.entries.set(key, {value, bytes}); this.bytes += bytes;
            while (this.bytes > this.limit || this.entries.size > this.maxEntries) {
                this.delete(this.entries.keys().next().value);
            }
            return value;
        }
        delete(key) {
            const entry = this.entries.get(key);
            if (entry) { this.bytes -= entry.bytes; this.entries.delete(key); }
        }
        clear() { this.entries.clear(); this.bytes = 0; }
    }
    const pixels = image => (image.naturalWidth || image.width || 0) * (image.naturalHeight || image.height || 0) * 4;
    const images = new BudgetCache(24 * MiB, 96);
    const animations = new BudgetCache(20 * MiB, 6);
    const terrain = new BudgetCache(24 * MiB, 64);
    const shadows = new BudgetCache(12 * MiB, 96);
    const lighting = new BudgetCache(16 * MiB, 768);
    const patterns = new BudgetCache(8 * MiB, 24);
    const pending = new Map();
    const failures = new Map();
    const queue = [];
    let active = 0;
    function pump() {
        while (active < 6 && queue.length) {
            const job = queue.shift(); active++;
            job().finally(() => { active--; pump(); });
        }
    }
    function decode(src) {
        return new Promise((resolve, reject) => {
            queue.push(async () => {
                const image = new Image(); image.decoding = 'async'; image.src = src;
                try { await image.decode(); resolve(image); }
                catch (error) { reject(error); }
            });
            pump();
        });
    }
    function image(src, invalidate) {
        if (!src) return null;
        let result = images.get(src);
        if (result) return result;
        result = new Image(); result.decoding = 'async';
        // Return a real loading Image so existing complete/naturalWidth guards work.
        result.src = src;
        images.set(src, result, 0);
        result.decode().then(() => {
            if (images.get(src) === result) images.set(src, result, pixels(result));
            if (invalidate) invalidate();
        }).catch(() => {});
        return result;
    }
    function frames(action, pose) {
        const key = `${action}/${pose}`;
        const cached = animations.get(key);
        if (cached) return cached;
        if ((failures.get(key) || 0) > Date.now()) return [];
        if (!pending.has(key)) {
            if (pending.size >= 3) return [];
            const count = action === 'idle' ? 12 : 16;
            const promise = Promise.all(Array.from({length: count}, (_, i) => {
                const pad = String(i).padStart(2, '0');
                return decode(window.CANVAS_ASSETS[`player_${action}_${pose}_${pad}`]);
            })).then(list => {
                animations.set(key, list, list.reduce((n, frame) => n + pixels(frame), 0));
            }).catch(error => {
                failures.set(key, Date.now() + 30000);
                console.warn('Animation unavailable:', key, error.message);
            })
                .finally(() => pending.delete(key));
            pending.set(key, promise);
        }
        // Publish only a fully decoded group; existing SVG art covers the loading interval.
        return [];
    }
    function lazyImage(owner, property, key, invalidate) {
        Object.defineProperty(owner, property, {configurable: true,
            get: () => image(window.CANVAS_ASSETS[key], invalidate)});
    }
    function lazyEnemy(owner, key, radius, gfx) {
        Object.defineProperty(owner, key, {configurable: true, get() {
            const sprite = gfx.createEnemySprite(key, radius);
            Object.defineProperty(owner, key, {configurable: true, value: sprite});
            return sprite;
        }});
    }
    function install(gfx) {
        const shadowIds = new WeakMap(); let nextShadowId = 1;
        gfx.getOrLoadCustomImage = src => image(src, () => gfx.invalidateTerrainCache());
        gfx.getOrLoadCustomPattern = (context, src) => {
            if (!src) return null;
            let pattern = patterns.get(src);
            if (pattern) return pattern;
            const source = image(src, () => gfx.invalidateTerrainCache());
            if (!source.complete || !source.naturalWidth) return null;
            pattern = context.createPattern(source, 'repeat');
            if (pattern) patterns.set(src, pattern, pixels(source));
            return pattern;
        };
        gfx.getShadowSilhouette = (key, source) => gfx.getImageShadowSilhouette(source);
        gfx.getImageShadowSilhouette = source => {
            if (!source || (source.tagName !== 'CANVAS' && (!source.complete || !source.naturalWidth))) return null;
            if (!shadowIds.has(source)) shadowIds.set(source, nextShadowId++);
            const key = shadowIds.get(source);
            let shadow = shadows.get(key);
            if (!shadow) {
                shadow = gfx.createShadowSilhouette(source, 1.5);
                if (shadow) shadows.set(key, shadow, pixels(shadow));
            }
            return shadow;
        };
        const invalidate = gfx.invalidateTerrainCache.bind(gfx);
        gfx.invalidateTerrainCache = () => { terrain.clear(); invalidate(); };
        const originalLight = gfx.applyDynamicLightingToStructure;
        const ids = new WeakMap(); let nextId = 1;
        gfx.applyDynamicLightingToStructure = function(context, x, y, radius, width, height, anchor, lights, isSprite = true, source = null, dx = null, dy = null) {
            if (!source || !isSprite || !lights?.length) return;
            if (source.tagName !== 'CANVAS' && (!source.complete || !source.naturalWidth)) return;
            const drawX = dx ?? -width / 2, drawY = dy ?? -(anchor ?? radius * 1.5);
            const mirror = context.getTransform().a < 0 ? -1 : 1;
            const near = [];
            for (const light of lights) {
                const lx = (light.x - x) * mirror, ly = light.y - y;
                const distance = Math.hypot(lx, ly), reach = width * .5 + light.r;
                if (distance < 5 || distance >= reach) continue;
                const attenuation = (1 - distance / reach) ** 2 * (light.intensity || .5);
                if (attenuation <= .02) continue;
                near.push({light, lx, ly, attenuation});
            }
            if (!near.length) return;
            near.sort((a, b) => b.attenuation - a.attenuation);
            near.length = Math.min(near.length, gfx.LIGHT_CFG.maxLights);
            // Quantize visual lighting only; physics and original sprite geometry stay exact.
            const normalized = near.map(({light, lx, ly}) => ({...light,
                x: Math.round(lx / 16) * 16, y: Math.round(ly / 16) * 16,
                intensity: Math.round((light.intensity || .5) * 32) / 32}));
            if (!ids.has(source)) ids.set(source, nextId++);
            const key = JSON.stringify([ids.get(source), width, height, drawX, drawY, gfx.LIGHT_CFG,
                normalized.map(l => [l.x, l.y, l.r, l.intensity, l.color])]);
            let layer = lighting.get(key);
            if (!layer) {
                layer = document.createElement('canvas');
                layer.width = Math.max(1, Math.ceil(width)); layer.height = Math.max(1, Math.ceil(height));
                const target = layer.getContext('2d'); target.translate(-drawX, -drawY);
                originalLight.call(gfx, target, 0, 0, radius, width, height, anchor, normalized, isSprite, source, drawX, drawY);
                lighting.set(key, layer, pixels(layer));
            }
            context.save(); context.globalCompositeOperation = 'lighter';
            context.drawImage(layer, drawX, drawY, width, height); context.restore();
        };
        gfx.cacheStats = () => Object.fromEntries(Object.entries({images, animations, terrain, shadows, lighting, patterns})
            .map(([name, cache]) => [name, {bytes: cache.bytes, limit: cache.limit,
                entries: cache.entries.size, hits: cache.hits, misses: cache.misses}]));
    }
    window.GameRuntime = {BudgetCache, image, frames, lazyImage, lazyEnemy, terrain, install};
})();
