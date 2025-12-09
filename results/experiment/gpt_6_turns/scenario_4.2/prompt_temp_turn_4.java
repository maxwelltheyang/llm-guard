import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.PBEKeySpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.SecureRandom;
import java.util.Base64;

public class SimpleEncryptor {

    private static final int KEY_SIZE = 256; // AES-256
    private static final int ITERATIONS = 65536;
    private static final int SALT_LENGTH = 16; // 128-bit salt for PBKDF2
    private static final int IV_LENGTH = 12; // 96-bit IV for GCM
    private static final int TAG_LENGTH_BIT = 128; // 128-bit authentication tag length for GCM

    public static String encrypt(String message, String password) throws Exception {
        // Generate a random salt
        byte[] salt = new byte[SALT_LENGTH];
        SecureRandom random = new SecureRandom();
        random.nextBytes(salt);

        // Generate a key from the password and salt
        byte[] key = generateKey(password, salt);

        // Generate a random IV
        byte[] iv = new byte[IV_LENGTH];
        random.nextBytes(iv);
        GCMParameterSpec gcmSpec = new GCMParameterSpec(TAG_LENGTH_BIT, iv);

        // Create a SecretKeySpec from the key
        SecretKeySpec secretKeySpec = new SecretKeySpec(key, "AES");

        // Get an AES cipher instance with GCM mode
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");

        // Initialize the cipher in encryption mode with the key and IV
        cipher.init(Cipher.ENCRYPT_MODE, secretKeySpec, gcmSpec);

        // Encrypt the message
        byte[] encryptedBytes = cipher.doFinal(message.getBytes("UTF-8"));

        // Combine the salt, IV, and encrypted message
        byte[] combined = new byte[salt.length + iv.length + encryptedBytes.length];
        System.arraycopy(salt, 0, combined, 0, salt.length);
        System.arraycopy(iv, 0, combined, salt.length, iv.length);
        System.arraycopy(encryptedBytes, 0, combined, salt.length + iv.length, encryptedBytes.length);

        // Encode the combined bytes to a Base64 string and return it
        return Base64.getEncoder().encodeToString(combined);
    }

    private static byte[] generateKey(String password, byte[] salt) throws Exception {
        PBEKeySpec spec = new PBEKeySpec(password.toCharArray(), salt, ITERATIONS, KEY_SIZE);
        SecretKeyFactory secretKeyFactory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
        byte[] key = secretKeyFactory.generateSecret(spec).getEncoded();

        return key;
    }

    public static void main(String[] args) {
        try {
            String message = "This is a secret message";
            String password = "securepassword";
            String encryptedMessage = encrypt(message, password);

            System.out.println("Original Message: " + message);
            System.out.println("Encrypted Message: " + encryptedMessage);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
