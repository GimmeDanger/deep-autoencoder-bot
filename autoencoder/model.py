import numpy as np
from skimage.transform import resize
from keras.optimizers import Adam
from keras.models import Model, Sequential
from keras.layers import Input, InputLayer, Dense, BatchNormalization, Dropout, Flatten, Reshape


class Autoencoder:
    def __init__(self, img_shape=(90, 90, 3), code_size=128, hidden_size=512,
                 encoder_weights_path = None, decoder_weights_path = None,
                 happiness_code_path = None):
        # Basic input parameters
        self.img_shape = img_shape
        self.code_size = code_size
        self.hidden_size = hidden_size
        self.encoder_weights_path = encoder_weights_path
        self.decoder_weights_path = decoder_weights_path
        self.happiness_code_path = happiness_code_path

        # Compile model
        self.encoder, self.decoder = self.build_autoencoder(img_shape, code_size, hidden_size)
        inp = Input(self.img_shape)
        code = self.encoder(inp)
        reconstruction = self.decoder(code)
        self.autoencoder = Model(inputs=inp, outputs=reconstruction)
        self.autoencoder.compile(optimizer=Adam(lr=0.0001), loss='binary_crossentropy')

        # Load weights and happiness code if needed
        if self.encoder_weights_path is not None and self.decoder_weights_path is not None:
            # load weights
            self.load_weights(self.encoder_weights_path, self.decoder_weights_path)            
            if self.happiness_code_path is not None:
              self.happiness_code = np.load(self.happiness_code_path)
              

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
    def _predict_code_reconstruction(self, code):
        # img[None] is the same as img[np.newaxis, :]
        return self.decoder.predict(code[None])[0]

    # \brief Load pretrained model weights
    def load_weights(self, encoder_weights_path, decoder_weights_path):
        self.encoder.load_weights(encoder_weights_path)
        self.decoder.load_weights(decoder_weights_path)
        
    # \brief Generate happy code from img code    
    def _get_happy_img_code(self, img_code, inverse):
        if inverse:
          happy_img_code = img_code - self.happiness_code
        else:
          happy_img_code = img_code + self.happiness_code
        return happy_img_code
        
    # \brief Add happiness to image    
    def _add_happiness(self, img, inverse):
        img_code = self.encoder.predict(img[None])[0]
        happy_img_code = self._get_happy_img_code(img_code, inverse)
        happy_img = self.decoder.predict(happy_img_code[None])[0]
        return happy_img
      
    # \brief Add happiness wrapper
    def add_happiness(self, raw_img, inverse=False):
        formatted_img = self.prepare_photo_before_feeding(raw_jpg)
        reconstr_img = self._add_happiness(formatted_img, inverse)
        return reconstr_img

    # \brief Photo must suit the input format of network
    def prepare_photo_before_feeding(self, raw_jpg):
        dx, dy = self.img_shape[0], self.img_shape[1]
        img = resize(raw_jpg, [dx, dy], mode='reflect', anti_aliasing=True)        
        # this method automatically normalizes by 255.
        # dimx, dimy = 3 * dx, 3 * dy
        #img = resize(raw_jpg, [dimx, dimy], mode='reflect', anti_aliasing=True)
        # crop the center part
        #img = img[dy:-dy, dx:-dx]
        # convert to float32, maybe redundant
        img = img.astype('float32')
        return img

    # \brief Feed network with raw_jpg
    def feed_photo(self, raw_jpg):
        formatted_img = self.prepare_photo_before_feeding(raw_jpg)
        reconstr_img = self.predict_img(formatted_img)
        return formatted_img, reconstr_img

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
