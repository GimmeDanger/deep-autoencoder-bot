import numpy as np
from keras.optimizers import Adam
from keras.models import Model, Sequential
from keras.layers import Input, InputLayer, Dense, BatchNormalization, Dropout, Flatten, Reshape


class Autoencoder:
    def __init__(self, img_shape=(90, 90, 3), code_size=128, hidden_size=512, load_default_pretrained_weights=False):
        # Basic input parameters
        self.img_shape = img_shape
        self.code_size = code_size
        self.hidden_size = hidden_size
        self.default_weights_folder = "model_weights"
        self.default_encoder_weights_path = f"{self.default_weights_folder}/encoder_weights.txt"
        self.default_decoder_weights_path = f"{self.default_weights_folder}/decoder_weights.txt"
        self.load_pretrained_weights = load_pretrained_weights

        # Compile model
        self.encoder, self.decoder = self.build_autoencoder(img_shape, code_size, hidden_size)
        inp = Input(self.img_shape)
        code = self.encoder(inp)
        reconstruction = self.decoder(code)
        self.autoencoder = Model(inputs=inp, outputs=reconstruction)
        self.autoencoder.compile(optimizer=Adam(lr=0.0001), loss='binary_crossentropy')

        # Load weights if needed
        if load_default_pretrained_weights:
            self.load_weights(self.default_encoder_weights_path, self.default_decoder_weights_path)

    # \brief Fit method wrapper
    # Note that y_train == x_train, y_val == x_val, because this is unsupervised learning model
    def fit(self, x_train, x_val, epochs, batch_size=128, verbose=1):
        self.autoencoder.fit(x=x_train, y=x_train, epochs=epochs, batch_size=batch_size,
                             validation_data=[x_val, x_val], verbose=verbose)

    # \brief Predict method wrapper
    def predict(self, data):
        assert np.min(data) >= 0 and np.max(data) <= 1
        return self.autoencoder.predict(data)

    # \brief Single image predict wrapper
    def predict_img(self, img):
        assert np.min(img) >= 0 and np.max(img) <= 1
        # img[None] is the same as img[np.newaxis, :]
        return self.autoencoder.predict(img[None])[0]

    # \brief Single code predict wrapper
    def predict_img_code(self, img):
        assert np.min(img) >= 0 and np.max(img) <= 1
        # img[None] is the same as img[np.newaxis, :]
        return self.encoder.predict(img[None])[0]

    # \brief Single code reconstruction predict wrapper
    def predict_code_reconstruction(self, code):
        # img[None] is the same as img[np.newaxis, :]
        return self.decoder.predict(code[None])[0]

    # \brief Load pretrained model weights
    def load_weights(self, encoder_weights_path=None, decoder_weights_path=None):
        if encoder_weights_path is None:
            encoder_weights_path = self.default_encoder_weights_path
        if decoder_weights_path is None:
            decoder_weights_path = self.default_decoder_weights_path
        self.encoder.load_weights(encoder_weights_path)
        self.decoder.load_weights(decoder_weights_path)

    # \brief Deep autoencoder network construction
    # \return encoder -- encoding part, which compress image to the code
    # \return decoder -- decoding part, which reconstruct image for input code
    @staticmethod
    def build_autoencoder(img_shape=(90, 90, 3), code_size=128, hidden_size=512):
        # encoder
        encoder = Sequential()
        encoder.add(InputLayer(img_shape))
        encoder.add(Flatten())
        encoder.add(Dense(hidden_size * 2, activation='relu'))
        encoder.add(BatchNormalization())
        encoder.add(Dropout(0.3))
        encoder.add(Dense(hidden_size, activation='relu'))
        encoder.add(BatchNormalization())
        encoder.add(Dropout(0.3))
        encoder.add(Dense(code_size, activation='relu'))
        # decoder
        decoder = Sequential()
        decoder.add(InputLayer((code_size,)))
        decoder.add(Dense(hidden_size, activation='relu'))
        decoder.add(BatchNormalization())
        decoder.add(Dropout(0.3))
        decoder.add(Dense(hidden_size * 2, activation='relu'))
        decoder.add(BatchNormalization())
        decoder.add(Dropout(0.3))
        decoder.add(Dense(img_shape[0] * img_shape[1] * img_shape[2], activation='sigmoid'))
        decoder.add(Reshape(img_shape))
        return encoder, decoder


'''
# test
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

def reconstruct_image(x,dims=(90,90,3)):
    img = x.reshape(*dims)*255.0
    #img = (img - np.min(img)) / (np.max(img) - np.min(img))
    return img

ae = Autoencoder()
ae.load_weights()
data = np.load('lfw_dataset/data_90.npy')
img = reconstruct_image(ae.predict_img(data[0]/255.))

from skimage.io import imsave
imsave('clean_img.jpg', data[0])
imsave('mod_img.jpg', img)
  
print("finished!")  
'''
