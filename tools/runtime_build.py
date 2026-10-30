"""Apply runtime integration to the extracted original HTML (not to edited output)."""
import re


def apply_runtime(html):
    def replace(old, new):
        nonlocal html
        if html.count(old) != 1:
            raise ValueError(f"Expected one integration point: {old[:80]}")
        html = html.replace(old, new, 1)

    replace('    <!-- === [MODULE: JS_CORE] === -->',
            '    <script src="runtime.js"></script>\n    <!-- === [MODULE: JS_CORE] === -->')
    # Hidden dialogue/portrait images should not compete with the lobby background.
    html = re.sub(r'<img\b(?![^>]*\bloading=)', '<img loading="lazy" decoding="async"', html)
    html = html.replace('<img loading="lazy" decoding="async" id="lobbyEmblemImg"',
                        '<img decoding="async" fetchpriority="high" id="lobbyEmblemImg"')
    start = html.index('                try {\n                    const tkc = new Image();')
    end = html.index('                // Pre-render các Sprite ánh sáng', start)
    world = {
        'tangKinhCacSprite': 'tang_kinh_cac_3d', 'luyenKhiBaoSprite': 'luyen_khi_bao_3d',
        'altarSprite': 'altar_platform_3d', 'turretBaseSprite': 'turret_base_3d',
        'turretCannonSprite': 'turret_cannon_3d', 'turretCannonSheet': 'turret_cannon_sheet',
        'thachDangSprite': 'thach_dang_3d', 'dinhHuongSprite': 'c_dinh_huong_3d',
        'thachTruSprite': 'thach_tru_phu_3d', 'spiritTreeSprite': 'co_thu_tien_canh_3d',
        'tienMonSprite': 'tien_mon_gate_3d', 'lotusPondSprite': 'celestial_lotus_pond_3d',
    }
    html = html[:start] + ''.join(
        f"                GameRuntime.lazyImage(this, '{prop}', '{key}', () => this.invalidateTerrainCache());\n"
        for prop, key in world.items()) + '\n' + html[end:]
    start = html.index('                animConfigs.forEach(cfg => {')
    end = html.index('                // Pre-render 10 chủng', start)
    html = html[:start] + '''                animConfigs.forEach(cfg => {
                    this.playerSprites[cfg.action] = {};
                    poses.forEach(pose => Object.defineProperty(this.playerSprites[cfg.action], pose, {
                        get: () => GameRuntime.frames(cfg.action, pose)
                    }));
                });

''' + html[end:]
    html = re.sub(r"this\.enemySprites\.(\w+) = this\.createEnemySprite\('\1', (\d+)\);",
                  r"GameRuntime.lazyEnemy(this.enemySprites, '\1', \2, this);", html)
    replace('        GFX.init();', '        GameRuntime.install(GFX);\n        GFX.init();')
    replace('            if (_ITEM_ICON_IMG_CACHE[iconId]) return _ITEM_ICON_IMG_CACHE[iconId];',
            '            return GameRuntime.image(getItemIconSrc(iconId));\n            /* legacy loader removed below */')
    start = html.index('            /* legacy loader removed below */')
    end = html.index('        window.getItemIconImage =', start)
    html = html[:start] + '        }\n' + html[end:]
    replace('        const _ITEM_ICON_IMG_CACHE = {};', '')
    replace('        function drawGame() {\n            const p = state.player;',
            '        function drawGame() {\n            if (state.inLobby) return;\n            const p = state.player;')
    # Shadow resolution follows its display size instead of retaining full source resolution.
    replace("                const w = isCanvas ? img.width : img.naturalWidth;\n                const h = isCanvas ? img.height : img.naturalHeight;",
            "                const sourceW = isCanvas ? img.width : img.naturalWidth;\n                const sourceH = isCanvas ? img.height : img.naturalHeight;\n                const shadowScale = Math.min(1, 512 / Math.max(sourceW, sourceH));\n                const w = Math.max(1, Math.round(sourceW * shadowScale));\n                const h = Math.max(1, Math.round(sourceH * shadowScale));")
    replace('                sctx.drawImage(img, 0, 0);', '                sctx.drawImage(img, 0, 0, w, h);')
    replace('bctx.filter = `blur(${blurRadius}px)`;', 'bctx.filter = `blur(${blurRadius * shadowScale}px)`;')
    start = html.index('                    const cacheKey = `${WORLD.baseTile}_')
    end = html.index('                    const lakes =', start)
    html = html[:start] + '''                    const qSize = 550;
                    const minQX = Math.max(0, Math.floor((camX - halfW) / qSize));
                    const maxQX = Math.min(7, Math.floor((camX + halfW) / qSize));
                    const minQY = Math.max(0, Math.floor((camY - halfH) / qSize));
                    const maxQY = Math.min(7, Math.floor((camY + halfH) / qSize));
                    const visibleCount = (maxQX - minQX + 1) * (maxQY - minQY + 1);
                    const resolution = visibleCount > 20 ? 0.5 : 1;
                    const cacheKey = `${WORLD.baseTile}_${(WORLD.buildings || []).length}_${(WORLD.customRoads || []).length}_${resolution}`;
                    if (this._terrainCacheKey !== cacheKey) {
                        GameRuntime.terrain.clear();
                        this._terrainCacheKey = cacheKey;
                    }
                    for (let qy = minQY; qy <= maxQY; qy++) {
                        for (let qx = minQX; qx <= maxQX; qx++) {
                            const key = `${qx},${qy}`;
                            let tile = GameRuntime.terrain.get(key);
                            if (!tile) {
                                tile = document.createElement('canvas');
                                tile.width = tile.height = Math.round(qSize * resolution);
                                const target = tile.getContext('2d'); target.scale(resolution, resolution);
                                this.bakeLushMeadowQuadrant(target, qx * qSize, qy * qSize, qSize, qSize);
                                GameRuntime.terrain.set(key, tile, tile.width * tile.height * 4);
                            }
                            ctx.drawImage(tile, qx * qSize, qy * qSize, qSize, qSize);
                        }
                    }

''' + html[end:]
    return html
