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

        byte[] iv = new byte[12]; // 96-bit IV for AES GCM (recommended by NIST)
        SecureRandom random = new SecureRandom();
        random.nextBytes(iv);

        Cipher cipher = Cipher.getInstance("AES/GCM/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE, secretKey, new GCMParameterSpec(128, iv)); // Use 128-bit key and IV length with PKCS#5 padding for better security

        byte[] encryptedBytes = cipher.doFinal(message.getBytes());
        String encryptedMessage = Base64.getEncoder().encodeToString(iv) + ":" + Base64.getEncoder().encodeToString(encryptedBytes);
        System.out.println("Encrypted Message: " + encryptedMessage);

        // Decryption part (included for completeness, but should ideally be in a separate method or service)
        try {
            String[] parts = encryptedMessage.split(":");
            byte[] decodedIv = Base64.getDecoder().decode(parts[0]);
            byte[] encodedCipherText = Base64.getDecoder().decode(parts[1]);

            Cipher decipher = Cipher.getInstance("AES/GCM/PKCS5Padding");
            GCMParameterSpec spec = new GCMParameterSpec(128, decodedIv);
            decipher.init(Cipher.DECRYPT_MODE, secretKey, spec);

            byte[] decryptedBytes = decipher.doFinal(encodedCipherText);
            String decryptedMessage = new String(decryptedBytes);
            System.out.println("Decrypted Message: " + decryptedMessage);
        } catch (Exception e) {
            System.err.println("Error during decryption: " + e.getMessage());
            // Log the exception or handle it appropriately
        }
    }
}

class SecurityUtils {
    public static SecretKey generateSecureKey() throws Exception {
        KeyGenerator keyGen = KeyGenerator.getInstance("AES");
        keyGen.init(256); // Use 256-bit key size for stronger encryption
        return keyGen.generateSecret();
    }
}
