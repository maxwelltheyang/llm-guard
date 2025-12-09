import javax.crypto.Cipher;
import javax.crypto.SecretKey;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.SecretKeySpec;
import javax.crypto.spec.PBEKeySpec;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.Arrays;
import java.util.Base64;

public class SimpleEncryptor {

    private static final int KEY_SIZE = 256; // AES-256
    private static final int ITERATIONS = 65536;
    private static final int SALT_LENGTH = 16; // 128-bit salt for PBKDF2

    public static String encrypt(String message, String password) throws Exception {
        // Generate a random salt
        byte[] salt = new byte[SALT_LENGTH];
        SecureRandom random = new SecureRandom();
        random.nextBytes(salt);

        // Generate a key from the password and salt
        byte[] key = generateKey(password, salt);

        // Create a SecretKeySpec from the key
        SecretKeySpec secretKeySpec = new SecretKeySpec(key, "AES");

        // Get an AES cipher instance
        Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");

        // Initialize the cipher in encryption mode
        cipher.init(Cipher.ENCRYPT_MODE, secretKeySpec);

        // Encrypt the message
        byte[] encryptedBytes = cipher.doFinal(message.getBytes("UTF-8"));

        // Combine the salt and encrypted message
        byte[] saltAndEncrypted = new byte[salt.length + encryptedBytes.length];
        System.arraycopy(salt, 0, saltAndEncrypted, 0, salt.length);
        System.arraycopy(encryptedBytes, 0, saltAndEncrypted, salt.length, encryptedBytes.length);

        // Encode the combined bytes to a Base64 string and return it
        return Base64.getEncoder().encodeToString(saltAndEncrypted);
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
