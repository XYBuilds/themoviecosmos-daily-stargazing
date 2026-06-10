# phase3.10 资源说明

output/Eval/phase3.10 在 SMB/NFS 上目录项损坏（无法 listdir / Explorer 显示为空），但子路径仍可访问。

请在本机资源管理器中打开同级目录 **phase3.10-visible** 浏览完整 346 个文件（obs 01–10、obs-fresh-labels、high-hit-score-review 等）。

修复空目录需在 NAS (192.168.1.110) 上删除损坏的 phase3.10 目录项后，再将 phase3.10-visible 移回 phase3.10。
