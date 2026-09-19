-- Load sidecar subtitles from the directory of a .strm playlist file.
-- mpv treats .strm as a playlist, so path/filename become the inner URL and
-- default sub-auto looks next to that URL instead of next to the .strm.
-- Syncplay starts mpv with --scripts-append pointing at this file.

local utils = require("mp.utils")
local msg = require("mp.msg")

local SUB_EXTS = {
    ass = true, srt = true, ssa = true, sub = true, vtt = true,
    idx = true, lrc = true, smi = true, sup = true,
}

local last_loaded_key = nil

local function basename(path)
    if not path then
        return nil
    end
    return path:match("[^/\\]+$")
end

local function dirname(path)
    if not path then
        return nil
    end
    return path:match("^(.*)[/\\]")
end

local function stem(name)
    if not name then
        return nil
    end
    return name:gsub("%.[^/.]+$", "")
end

local function extension(name)
    if not name then
        return nil
    end
    return name:lower():match("%.([^.]+)$")
end

local function is_matching_sidecar(strm_stem, filename)
    local ext = extension(filename)
    if not ext or not SUB_EXTS[ext] then
        return false
    end
    local file_stem = stem(filename)
    if file_stem == strm_stem then
        return true
    end
    local prefix = strm_stem .. "."
    return file_stem:sub(1, #prefix) == prefix
end

local function is_strm(path)
    return path and path:lower():match("%.strm$")
end

local function load_sidecars()
    -- Same rules as syncplay.strm.decide_sidecar_load.
    local playlist_path = mp.get_property("playlist-path")
    local path = mp.get_property("path")
    if not is_strm(playlist_path) then
        return
    end
    if not path or is_strm(path) then
        msg.verbose("strm-sidecars: waiting for inner file")
        return
    end
    local key = playlist_path .. "\0" .. path
    if key == last_loaded_key then
        return
    end

    local dir = dirname(playlist_path)
    local strm_stem = stem(basename(playlist_path))
    if not dir or not strm_stem then
        return
    end

    local files = utils.readdir(dir, "files")
    if not files then
        msg.warn("strm-sidecars: cannot read " .. dir)
        return
    end

    last_loaded_key = key

    local loaded = 0
    for _, filename in ipairs(files) do
        if is_matching_sidecar(strm_stem, filename) then
            local full = utils.join_path(dir, filename)
            local flags = (loaded == 0) and "select" or "auto"
            mp.commandv("sub-add", full, flags)
            loaded = loaded + 1
            msg.info("strm-sidecars: added " .. full)
        end
    end
    if loaded == 0 then
        msg.verbose("strm-sidecars: no sidecars next to " .. playlist_path)
    end
end

mp.register_event("file-loaded", load_sidecars)
mp.observe_property("playlist-path", "string", function()
    load_sidecars()
end)
mp.observe_property("path", "string", function()
    load_sidecars()
end)
