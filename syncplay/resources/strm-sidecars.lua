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

local last_playlist_path = nil

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

local function load_sidecars(playlist_path)
    if not playlist_path or playlist_path == last_playlist_path then
        return
    end
    if not playlist_path:lower():match("%.strm$") then
        last_playlist_path = playlist_path
        return
    end
    last_playlist_path = playlist_path

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

    local loaded = 0
    for _, filename in ipairs(files) do
        if is_matching_sidecar(strm_stem, filename) then
            local full = utils.join_path(dir, filename)
            mp.commandv("sub-add", full, "auto")
            loaded = loaded + 1
            msg.info("strm-sidecars: added " .. full)
        end
    end
    if loaded == 0 then
        msg.verbose("strm-sidecars: no sidecars next to " .. playlist_path)
    end
end

mp.observe_property("playlist-path", "string", function(_, value)
    load_sidecars(value)
end)
mp.register_event("start-file", function()
    load_sidecars(mp.get_property("playlist-path"))
end)
