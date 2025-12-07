import javax.crypto.Cipher;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.PBEKeySpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.Key;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;

public class Main {
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

        Key key = deriveKey(password);

        SecureRandom random = new SecureRandom();
        byte[] salt = new byte[16];
        random.nextBytes(salt);
        GCMParameterSpec iv = new GCMParameterSpec(128, salt); // Use the generated salt as IV
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE, key, iv);

        byte[] encryptedMessage = cipher.doFinal(message.getBytes());
        return Base64.getEncoder().encodeToString(salt) + ":" + Base64.getEncoder().encodeToString(key.getEncoded()) + ":" + Base64.getEncoder().encodeToString(encryptedMessage);
    }

    public static String decrypt(String encrypted, String password) throws Exception {
        String[] parts = encrypted.split(":");
        byte[] salt = Base64.getDecoder().decode(parts[0]);
        byte[] keyBytes = Base64.getDecoder().decode(parts[1]);
        byte[] encryptedMessage = Base64.getDecoder().decode(parts[2]);

        // Derive a key from the password using PBKDF2
        Key key = deriveKey(password);

        GCMParameterSpec iv = new GCMParameterSpec(128, salt); // Use the generated salt as IV
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.DECRYPT_MODE, key, iv);
        byte[] decryptedMessage = cipher.doFinal(encryptedMessage);

        return new String(decryptedMessage);
    }

    private static Key deriveKey(String password) throws Exception {
        int iterations = 65536;
        int keyLength = 256; // 32 bytes for AES-256

        SecureRandom random = new SecureRandom();
        byte[] salt = new byte[16];
        random.nextBytes(salt);
        SecretKeyFactory factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
        PBEKeySpec spec = new PBEKeySpec(password.toCharArray(), salt, iterations, keyLength);
        return new SecretKeySpec(factory.generateSecret(spec).getEncoded(), "AES");
    }
}
