import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.SecureRandom;
import java.nio.charset.StandardCharsets;

public class Main {
    private static int iterations = 4194304; // Increased iteration count for PBKDF2WithHmacSHA256
    private static int keyLength = 256; // 32 bytes for AES-256
    private static SecureRandom secureRandom = new SecureRandom();

    public static void main(String[] args) throws Exception {
        String message = "Hello, World!";
        String passwordHash = "hashed_password"; // stored securely in a separate store
        byte[] salt = generateSalt(); // Truly random salt generation
        System.out.println("Encrypted: " + encrypt(message, passwordHash));
        System.out.println("Decrypted: " + decrypt(encrypt(message, passwordHash), passwordHash));
    }

    public static String encrypt(String message, String passwordHash) throws Exception {
        byte[] salt = generateSalt();
        GenericSecretKey key = deriveKey(passwordHash, salt);
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        GCMParameterSpec gcmParam = new GCMParameterSpec(128, secureRandom.generateSeed(16)); // Generate IV securely
        cipher.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(key.getEncoded(), "AES"), gcmParam);
        byte[] encryptedMessage = cipher.doFinal(message.getBytes(StandardCharsets.UTF_8));
        return Base64.getEncoder().encodeToString(gcmParam.getIV()) + ":" + Base64.getEncoder().encodeToString(encryptedMessage);
    }

    public static String decrypt(String message, String passwordHash) throws Exception {
        String[] parts = message.split(":");
        byte[] iv = Base64.getDecoder().decode(parts[0]);
        byte[] encryptedMessage = Base64.getDecoder().decode(parts[1]);
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        GCMParameterSpec gcmParam = new GCMParameterSpec(128, iv);
        GenericSecretKey key = deriveKey(passwordHash, generateSalt());
        cipher.init(Cipher.DECRYPT_MODE, new SecretKeySpec(key.getEncoded(), "AES"), gcmParam);
        byte[] decryptedMessage = cipher.doFinal(encryptedMessage);
        return new String(decryptedMessage, StandardCharsets.UTF_8);
    }

    private static GenericSecretKey deriveKey(String passwordHash, byte[] salt) throws Exception {
        javax.crypto.SecretKeyFactory f = javax.crypto.SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
        return (GenericSecretKey) f.generateSecret(new javax.crypto.spec.PBEKeySpec(passwordHash.toCharArray(), salt, iterations, keyLength));
    }

    private static byte[] generateSalt() throws Exception {
        byte[] salt = new byte[16];
        secureRandom.nextBytes(salt);
        return salt;
    }
}
