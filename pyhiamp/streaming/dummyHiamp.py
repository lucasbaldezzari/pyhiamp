import numpy as np
import pylsl
import time

class dummyHiamp:
    """
    Class for generating a dummy Hiamp.
    It is mainly used for testing and development.
    Generates a synthetic EEG signal at a given sampling frequency and a given number of channels.
    The class is designed to be used with the LSL (Lab Streaming Layer) library for streaming data.
    The generated signal is a random signal with a Gaussian distribution or a sine wave per channel.
    You can add metadata to the stream and rename channels.
    The class also allows you to scale the signal.
    """
    def __init__(self, name="DummyHIAMP", stream_type="eeg",srate=512, channels_names:list=None,
                 channel_format="float32", source_id="DummyHiamp2025", channel_locations:list=None):
        """
        Constructor for the dummy Hiamp class.

        Parameters:
        - name: Name of the stream.
        - stream_type: Type of the stream. Default is "eeg".
        - srate: Sampling frequency. Default is 512 Hz.
        - channels: Number of channels. Default is 62.
        - channels_names: List of channel names (e.g., ["Cz"]). Default is None.
        - channels_positions: List of channel positions (e.g., [[-0.0742, 0, 0.0668],]). Default is None.
        """

        self.scale = 1.0
        self.name = name
        self.srate = srate
        self.stream_type = stream_type
        self.channels_names = channels_names
        self.n_channels = len(channels_names)
        self.channel_format = channel_format
        self.source_id = source_id
        self.channel_locations = channel_locations

        self.info = pylsl.StreamInfo(self.name, self.stream_type, self.n_channels, self.srate,
                                     channel_format=channel_format, source_id=self.source_id)
        
        ##setting info metadata by default. If you want to change it, you can call
        self.addManufacterMetadata()
        self.addChannelMetadata()
        self.addCapMetadata()

    def __call__(self):
        pass

    def addManufacterMetadata(self):
        self.info.desc().append_child_value("manufacturer", "DummyHiamp")

    def addChannelMetadata(self, unit="microvolts", scaling_factor=1.0, type="eeg"):
        chns = self.info.desc().append_child("channels")
        for chan_ix, label in enumerate(self.channels_names):
            ch = chns.append_child("channel")
            ch.append_child_value("label", label)
            ch.append_child_value("unit", unit)
            ch.append_child_value("type", type)
            ch.append_child_value("scaling_factor", str(scaling_factor))
            if self.channel_locations:
                loc = ch.append_child("location")
                for ax_str, pos in zip(["X", "Y", "Z"], self.channel_locations[chan_ix]):
                    loc.append_child_value(ax_str, str(pos))

    def addCapMetadata(self, name="DummyCap", size="M", labelscheme="10-20"):
        """
        Add cap metadata to the stream.

        Parameters:
        - name: Name of the cap. Default is "DummyCap".
        - size: Size of the cap. Default is "M".
        - labelscheme: Label scheme of the cap. Default is "10-20".
        """
        cap = self.info.desc().append_child("cap")
        cap.append_child_value("name", name)
        cap.append_child_value("size", size)
        cap.append_child_value("labelscheme", labelscheme)


    def startStreaming(self,chunk_size=32, sleep=0.01, total_time = 60, delay=0.0, terminate=True, **kwargs):
        """
        Starting the streaming of the dummy Hiamp.

        Parameters:
        - chunk_size (int): Size of the chunk to send. Default is 32 samples.
        - sleep (float): Delay in seconds. Default is 0.01 seconds.
        - total_time (int): Total time in seconds. Default is 60 seconds.
        - delay (float): Delay in seconds. Default is 0.0 seconds. This is used to simulate the delay of the signal e.g., as if coming from some external hardware with known latency.
        - terminate (bool): If True, the stream will be terminated after the total time. Default is True.
        - kwargs: Additional arguments to pass to the _getSyntheticEEG method.
        """
        total_time=int(total_time)
        self.outlet = pylsl.StreamOutlet(self.info, chunk_size, total_time)
        print(f"Now sending data for {total_time} seconds...")
        start_time = pylsl.local_clock()
        sent_samples = 0
        while True:
            elapsed_time = pylsl.local_clock() - start_time
            required_samples = int(self.srate * elapsed_time) - sent_samples
            if required_samples > 0:
                # if the required samples are more than the chunk size, we need to send them in chunks

                mychunk=self._getSyntheticEEG(required_samples, **kwargs)
                stamp = pylsl.local_clock() - delay
                # now send it and wait for a bit
                self.outlet.push_chunk(mychunk, stamp)
                sent_samples += required_samples

            if elapsed_time > total_time:
                break

            time.sleep(sleep)
        self.chunk = mychunk

        print(f"Finished streaming. Total time: {round(elapsed_time,5)} seconds.")
        if terminate:
            del self.outlet
            print("Stream outlet deleted.")

    def _getSyntheticEEG(self, n_samples, peak_freq=14, fwhm=15):
        """
        This function generates a synthetic EEG signal using a Gaussian distribution.
        The signal is generated using the inverse Fourier transform of a random spectrum.
        The spectrum is generated using a Gaussian distribution with a given peak frequency and full width at half maximum (FWHM).

        Parameters:
        - n_samples: Number of samples to generate.
        - peak_freq: Peak frequency of the Gaussian distribution. Default is 14 Hz.
        - fwhm: Full width at half maximum (FWHM) of the Gaussian distribution. Default is 15 Hz.
        """

        hz = np.linspace(0,self.srate,n_samples) #frequencies
        s = fwhm*(2*np.pi-1)/(4*np.pi) #normalized width
        x  = hz-peak_freq #shifted frequencies
        gauss = np.exp((-.5)*(x/s)**2) #gaussian

        ##nd.array with shape channels x required_samples
        data = np.zeros((self.n_channels, n_samples))
        for ch in range(self.n_channels):
            #fourier coefficients for the random spectrum
            fc = np.random.rand(n_samples)*np.exp(2j*np.pi*np.random.rand(n_samples))
            fc = fc*gauss
            #inverse fourier transform to get the signal
            data[ch] = np.fft.ifft(fc).real

        data*=self.scale #scaling the signal

        return data.T.tolist() #returning a list of lists, where each list is a channel with the samples

    def rename_channels(self, mapping:dict):
        """
        Set the channel names.

        Parameters:
        - mapping: Dictionary with the mapping of the channels. The keys are the old names and the values are the new names (e.g., {'CH1':"Fz"}).
        """
        pass


    def addMetaData(self, metadata:dict):
        """
        Add metadata to the stream.

        Parameters:
        - metadata: Dictionary with the metadata to add. The keys are the names of the metadata and the values are the values of the metadata (e.g., {'subject':"S1"}).
        """
        pass

if __name__ == "__main__":
    # Example usage of the dummy Hiamp class.
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