import javax.crypto.Cipher;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.PBEKeySpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.Key;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;

public class Main {
    private static byte[] storedSalt = new byte[16];
    private static int saltIndex = 0;

    public static void main(String[] args) throws Exception {
        String message = "Hello, World!";
        String password = "mysecretpassword";
        System.out.println("Encrypted: " + encrypt(message, password));
        System.out.println("Decrypted: " + decrypt(encrypt(message, password), password));
    }

    public static String encrypt(String message, String password) throws Exception {
        // Derive a key from the password using Argon2id
        int iterations = 65536;
        int keyLength = 256; // 32 bytes for AES-256

        GCMParameterSpec iv = new GCMParameterSpec(128, storedSalt); // Use the stored salt as IV
        Key key = deriveKey(password, storedSalt);

        Cipher cipher = Cipher.getInstance("AES/GCM");
        cipher.init(Cipher.ENCRYPT_MODE, key, iv);

        byte[] encryptedMessage = cipher.doFinal(message.getBytes());
        return Base64.getEncoder().encodeToString(iv.getIV()) + ":" + Base64.getEncoder().encodeToString(encryptedMessage);
    }

    public static String decrypt(String encrypted, String password) throws Exception {
        String[] parts = encrypted.split(":");
        byte[] ivBytes = Base64.getDecoder().decode(parts[0]);
        byte[] encryptedMessage = Base64.getDecoder().decode(parts[1]);

        // Derive a key from the password using Argon2id
        Key key = deriveKey(password, ivBytes);

        GCMParameterSpec iv = new GCMParameterSpec(128, ivBytes); // Use the stored IV as IV
        Cipher cipher = Cipher.getInstance("AES/GCM");
        cipher.init(Cipher.DECRYPT_MODE, key, iv);
        byte[] decryptedMessage = cipher.doFinal(encryptedMessage);

        return new String(decryptedMessage);
    }

    private static Key deriveKey(String password, byte[] salt) throws Exception {
        int iterations = 65536;
        int keyLength = 256; // 32 bytes for AES-256

        SecretKeyFactory factory = SecretKeyFactory.getInstance("Argon2id");
        PBEKeySpec spec = new PBEKeySpec(password.toCharArray(), salt, iterations, keyLength);
        return new SecretKeySpec(factory.generateSecret(spec).getEncoded(), "AES");
    }
}
