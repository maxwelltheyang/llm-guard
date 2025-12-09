import javax.crypto.Cipher;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.PBEKeySpec;
import java.security.Key;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.util.Base64;

public class Main {
    public static void main(String[] args) throws Exception {
        String message = "Hello, World!";
        String password = "mysecretpassword";
        System.out.println(encrypt(message, password));
    }

    public static String encrypt(String message, String password) throws Exception {
        // Derive a key from the password using PBKDF2
        byte[] salt = new byte[16];
        SecureRandom secureRandom = new SecureRandom();
        secureRandom.nextBytes(salt);
        int iterations = 65536;
        int keyLength = 256; // 32 bytes for AES-256

        Key key = deriveKey(password, salt, iterations, keyLength);

        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        GCMParameterSpec iv = new GCMParameterSpec(128, salt); // Use the derived salt as IV
        cipher.init(Cipher.ENCRYPT_MODE, key, iv);
        byte[] encryptedMessage = cipher.doFinal(message.getBytes());
        return Base64.getEncoder().encodeToString(encryptedMessage);
    }

    private static Key deriveKey(String password, byte[] salt, int iterations, int keyLength) throws Exception {
        SecretKeyFactory factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
        PBEKeySpec spec = new PBEKeySpec(password.toCharArray(), salt, iterations, keyLength);
        return factory.generateSecret(spec);
    }
}
