from pyhiamp.streaming.dummyHiamp import dummyHiamp
import pandas as pd
chans_info_df = pd.read_csv("_hide_docs\\examples\\ghiamp_montage.sfp",header=None, sep="\t",names=["label","X","Y","Z"])
channels_names = chans_info_df["label"].tolist()
channel_locations = chans_info_df[["X","Y","Z"]].values.tolist()

hiamp = dummyHiamp(name="DummyHiamp", stream_type="eeg", srate=512, channels_names=channels_names,
                    channel_format="float32", source_id="DummyHiamp2025",
                    channel_locations=channel_locations)

print(hiamp.info.name())
print(hiamp.info.type())
print(hiamp.info.channel_format())
print(hiamp.info.channel_count())
print(hiamp.info.nominal_srate())
print(hiamp.info.source_id())
# print(hiamp.info.as_xml())
hiamp.scale = 30
hiamp.startStreaming(chunk_size=64, sleep=0.01, total_time=5, delay=0.0,terminate=True,
                        peak_freq=14, fwhm=15)
print("Finished script.")