import org.bouncycastle.jce.provider.BouncyCastleProvider;
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.SecureRandom;
import java.util.Base64;

public class AESEncryption {

    // Method to encrypt the data using AES/GCM mode with BouncyCastle provider
    public static String encrypt(String data, String key) throws Exception {
        // Register the BouncyCastle provider
        Security.addProvider(new BouncyCastleProvider());

        // Generate a random nonce
        byte[] nonce = new byte[12];
        SecureRandom secureRandom = new SecureRandom();
        secureRandom.nextBytes(nonce);

        // Create a SecretKeySpec from the key bytes
        SecretKeySpec secretKeySpec = new SecretKeySpec(key.getBytes(), "AES");

        // Initialize cipher with AES/GCM mode and BouncyCastle provider
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        GCMParameterSpec spec = new GCMParameterSpec(128, nonce);
        cipher.init(Cipher.ENCRYPT_MODE, secretKeySpec, spec);

        // Encrypt the data
        byte[] encryptedData = cipher.doFinal(data.getBytes());

        // Combine the nonce and encrypted data into a single byte array
        byte[] combinedData = new byte[nonce.length + encryptedData.length];
        System.arraycopy(nonce, 0, combinedData, 0, nonce.length);
        System.arraycopy(encryptedData, 0, combinedData, nonce.length, encryptedData.length);

        // Encode the combined data with Base64 for easier transmission and storage
        return Base64.getEncoder().encodeToString(combinedData);
    }

    // Method to decrypt the data using AES/GCM mode with BouncyCastle provider
    public static String decrypt(String encodedData, String key) throws Exception {
        // Decode the Base64 encoded data into a byte array
        byte[] combinedData = Base64.getDecoder().decode(encodedData);

        // Extract the nonce from the combined data
        byte[] nonce = new byte[12];
        System.arraycopy(combinedData, 0, nonce, 0, 12);

        // Extract the encrypted data from the combined data
        byte[] encryptedData = new byte[combinedData.length - 12];
        System.arraycopy(combinedData, 12, encryptedData, 0, encryptedData.length);

        // Create a SecretKeySpec from the key bytes
        SecretKeySpec secretKeySpec = new SecretKeySpec(key.getBytes(), "AES");

        // Initialize cipher with AES/GCM mode and BouncyCastle provider
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        GCMParameterSpec spec = new GCMParameterSpec(128, nonce);
        cipher.init(Cipher.DECRYPT_MODE, secretKeySpec, spec);

        // Decrypt the data
        byte[] decryptedData = cipher.doFinal(encryptedData);

        // Return the decrypted string
        return new String(decryptedData);
    }

    public static void main(String[] args) {
        try {
            String message = "Hello, World!";
            String password = "ThisIsASecretPassword";

            // Encrypt the message
            String encodedData = encrypt(message, password);
            System.out.println("Encrypted Data: " + encodedData);

            // Decrypt the message
            String decryptedMessage = decrypt(encodedData, password);
            System.out.println("Decrypted Message: " + decryptedMessage);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
