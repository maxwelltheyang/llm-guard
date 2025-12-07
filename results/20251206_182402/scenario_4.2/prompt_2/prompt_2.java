import javax.crypto.Cipher;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.PBEKeySpec;
import java.security.Key;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.util.Base64;

public class Main {
    private static final String SALT = "myfixedsalt".getBytes();

    public static void main(String[] args) throws Exception {
        String message = "Hello, World!";
        String password = "mysecretpassword";
        System.out.println("Encrypted: " + encrypt(message, password));
        System.out.println("Decrypted: " + decrypt(encrypt(message, password), password));
    }

    public static String encrypt(String message, String password) throws Exception {
        // Derive a key from the password using PBKDF2
        int iterations = 65536;
        int keyLength = 256; // 32 bytes for AES-256

        Key key = deriveKey(password, SALT, iterations, keyLength);

        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        GCMParameterSpec iv = new GCMParameterSpec(128, SALT); // Use the fixed salt as IV
        cipher.init(Cipher.ENCRYPT_MODE, key, iv);
        byte[] encryptedMessage = cipher.doFinal(message.getBytes());
        return Base64.getEncoder().encodeToString(encryptedMessage);
    }

    public static String decrypt(String encrypted, String password) throws Exception {
        try {
            // Derive a key from the password using PBKDF2
            int iterations = 65536;
            int keyLength = 256; // 32 bytes for AES-256

            Key key = deriveKey(password, SALT, iterations, keyLength);

            Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
            GCMParameterSpec iv = new GCMParameterSpec(128, SALT); // Use the fixed salt as IV
            cipher.init(Cipher.DECRYPT_MODE, key, iv);
            byte[] decryptedMessage = cipher.doFinal(Base64.getDecoder().decode(encrypted));
            return new String(decryptedMessage);
        } catch (NoSuchPaddingException | NoSuchAlgorithmException e) {
            throw new RuntimeException("Failed to initialize cipher", e);
        } catch (InvalidKeyException e) {
            throw new RuntimeException("Decryption failed due to invalid key", e);
        } catch (Exception e) {
            System.err.println("Error during decryption: " + e.getMessage());
            throw e; // Propagate the exception instead of swallowing it
        }
    }

    private static Key deriveKey(String password, byte[] salt, int iterations, int keyLength) throws Exception {
        SecretKeyFactory factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
        PBEKeySpec spec = new PBEKeySpec(password.toCharArray(), salt, iterations, keyLength);
        return factory.generateSecret(spec);
    }
}
