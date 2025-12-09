import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import java.util.Base64;
import java.security.SecureRandom;

public class SecureEncryption {
    public static void main(String[] args) throws Exception {
        String message = "Hello, World!";
        SecretKey secretKey = SecurityUtils.generateSecureKey(); // Use a secure key management utility

        byte[] iv = new byte[16]; // 128-bit IV for AES GCM
        SecureRandom random = new SecureRandom();
        random.nextBytes(iv);

        Cipher cipher = Cipher.getInstance("AES/GCM/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE, secretKey, new GCMParameterSpec(128, iv)); // Use 128-bit key and IV length with PKCS5Padding

        byte[] encryptedBytes = cipher.doFinal(message.getBytes());
        String encryptedMessage = Base64.getEncoder().encodeToString(iv) + ":" + Base64.getEncoder().encodeToString(encryptedBytes);
        System.out.println("Encrypted Message: " + encryptedMessage);

        // Decrypt the message to verify it's reversible
        String[] parts = encryptedMessage.split(":");
        byte[] decodedIv = Base64.getDecoder().decode(parts[0]);
        byte[] encodedCipherText = Base64.getDecoder().decode(parts[1]);

        Cipher decipher = Cipher.getInstance("AES/GCM/PKCS5Padding");
        GCMParameterSpec spec = new GCMParameterSpec(128, decodedIv);
        decipher.init(Cipher.DECRYPT_MODE, secretKey, spec);

        byte[] decryptedBytes = decipher.doFinal(encodedCipherText);
        String decryptedMessage = new String(decryptedBytes);
        System.out.println("Decrypted Message: " + decryptedMessage);
    }
}

class SecurityUtils {
    public static SecretKey generateSecureKey() throws Exception {
        // Implement a secure key generation and management system here
        KeyGenerator keyGen = KeyGenerator.getInstance("AES");
        keyGen.init(128); // Use 128-bit key size
        return keyGen.generateSecret();
    }
}
