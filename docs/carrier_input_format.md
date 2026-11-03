# Carrier input

每个 sequence 一个 UTF-8 逗号分隔 MOT 文件 `<sequence>.txt`，至少七列：frame, original_ID, left, top, width, height, confidence；其余字段按原始 token 保留。帧号从媒体的第一个实际帧对应1开始，ID和帧号为整数值，bbox是像素 tlwh。confidence按文件值使用，不重估。路径配置显式指定 sequence 和 FPS，不从 GT 得到。

同一 sequence 和原ID按frame排序构建 completed tracklet，内部缺帧不拆分。SportsMOT两载体和SoccerNet至少2个观测可关联；TeamTrack允许1个。原始行不排序写回，所有不合格轨迹行仍在预测内。新增包装器对非finite前七字段和重复原始(frame,ID)明确报错；这是入口校验，不改变冻结关联器的定义。原载体必须有正确媒体对应，不能把不同detector/tracker输出互换。

JPEG模式优先6位帧文件名，不存在才尝试8位；TeamTrack从img1.mp4连续解码而非seek或按FPS重采样。TeamTrack协议FPS与某些MP4容器FPS可能不同，配置保留原关联协议，不静默换成容器速率。

负尺寸或不符合原缓存area契约的框可能被冻结frontend校验拒绝；入口不修正原框。TeamTrack原行顺序在同一ID内须与时间排序兼容，冻结frontend会核对每个frame；不通过重排缓存或修改原行来掩盖不兼容输入。真实实验Carrier已全量通过映射核对。
